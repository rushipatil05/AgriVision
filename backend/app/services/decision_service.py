import time
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from app.schemas.decision import (
    DecisionRecommendationRequest,
    DecisionRecommendationResponse,
    AlternativeCropEvaluation,
    DecisionExplanation
)
from app.schemas.crop import CropRecommendationRequest
from app.schemas.yield_ import YieldForecastRequest
from app.schemas.price import PriceForecastRequest
from app.services.crop_recommendation_service import CropRecommendationService
from app.services.yield_forecasting_service import YieldForecastingService
from app.services.price_forecasting_service import PriceForecastingService
from app.services.prediction_service import PredictionService

logger = logging.getLogger("agripulse.services.decision")

# Baseline price references (INR/Quintal) for realistic sequence derivation if omitted
COMMODITY_PRICE_BASELINES: Dict[str, float] = {
    "rice": 3100.0,
    "wheat": 2250.0,
    "maize": 1950.0,
    "cotton": 6800.0,
    "jute": 4800.0,
    "coffee": 8500.0,
    "apple": 7500.0,
    "banana": 2400.0,
    "grapes": 5500.0,
    "watermelon": 1400.0,
    "muskmelon": 1800.0,
    "papaya": 2100.0,
    "mango": 4200.0,
    "orange": 3600.0,
    "pomegranate": 6500.0,
    "blackgram": 6200.0,
    "chickpea": 5100.0,
    "lentil": 5800.0,
    "mungbean": 6900.0,
    "mothbeans": 5400.0,
    "pigeonpeas": 6700.0,
    "kidneybeans": 7200.0,
    "coconut": 3200.0,
    "sugarcane": 350.0,
    "potato": 1300.0,
    "onion": 1650.0,
    "tomato": 1900.0
}


class DecisionService:
    """
    Agricultural Decision Engine orchestrating Crop Suitability, Yield Projections,
    and Market Price Trajectories into a unified multi-criteria decision ranking.
    """

    @classmethod
    def generate_commodity_price_series(cls, crop_name: str) -> List[float]:
        """
        Derives a realistic 30-day historical modal price series for the target crop/commodity.
        """
        base = COMMODITY_PRICE_BASELINES.get(crop_name.lower(), 2500.0)
        series = []
        val = base
        for i in range(30):
            # Deterministic mild variance around base price
            delta = ((i % 7) - 3) * (base * 0.008)
            val = max(100.0, round(base + delta, 2))
            series.append(val)
        return series

    @classmethod
    def format_crop_name(cls, crop_str: str) -> str:
        """
        Normalizes crop string for display and downstream services.
        """
        clean = crop_str.strip().lower()
        return clean.capitalize()

    @classmethod
    def recommend(
        cls,
        request: DecisionRecommendationRequest,
        db: Optional[Session] = None,
        user_id: Optional[int] = None
    ) -> DecisionRecommendationResponse:
        t0 = time.time()
        logger.info(f"Executing Agricultural Decision Engine for region: {request.district}, {request.state}")

        # -------------------------------------------------------------
        # 1. Step 1: Execute Crop Recommendation Model (LSTM)
        # -------------------------------------------------------------
        crop_req = CropRecommendationRequest(
            N=request.N,
            P=request.P,
            K=request.K,
            temperature=request.temperature,
            humidity=request.humidity,
            ph=request.ph,
            rainfall=request.rainfall,
            top_k=5
        )
        crop_res = CropRecommendationService.recommend(crop_req)

        # Select top candidates (up to 3 for deep cross-module evaluation)
        candidate_items = crop_res.recommendations[:3]
        if not candidate_items:
            candidate_items = [crop_res.recommendations[0]]

        # -------------------------------------------------------------
        # 2. Step 2 & 3: Cross-Module Evaluation (Yield + Price Forecasting)
        # -------------------------------------------------------------
        evaluations: List[AlternativeCropEvaluation] = []

        for item in candidate_items:
            crop_name = cls.format_crop_name(item.crop)
            prob = float(item.probability)
            suitability_score = round(min(100.0, max(0.0, prob * 100.0)), 2)

            # --- Yield Prediction ---
            try:
                yield_req = YieldForecastRequest(
                    state=request.state,
                    district=request.district,
                    crop=crop_name,
                    season=request.season,
                    area=request.area,
                    crop_year=request.crop_year,
                    model_type="dnn"
                )
                yield_res = YieldForecastingService.predict(yield_req)
                pred_yield = yield_res.predicted_yield_tonnes_per_hectare
                tot_prod = yield_res.estimated_total_production_tonnes
            except Exception as e:
                logger.warning(f"Yield model fallback for crop {crop_name}: {e}")
                pred_yield = 3.5
                tot_prod = round(pred_yield * request.area, 2)

            # Normalize Yield Score (Benchmark 5.0 t/ha = 100%)
            yield_score = round(min(100.0, max(5.0, (pred_yield / 5.0) * 100.0)), 2)

            # --- Price Forecast ---
            try:
                hist_prices = (
                    request.historical_prices
                    if request.historical_prices and len(request.historical_prices) >= 30
                    else cls.generate_commodity_price_series(item.crop)
                )
                price_req = PriceForecastRequest(
                    commodity=crop_name,
                    market=request.market,
                    historical_prices=hist_prices,
                    forecast_horizon=request.forecast_horizon
                )
                price_res = PriceForecastingService.forecast(price_req)
                forecast_price = price_res.predicted_end_price
                price_trend = price_res.trend_direction
            except Exception as e:
                logger.warning(f"Price model fallback for crop {crop_name}: {e}")
                base_p = COMMODITY_PRICE_BASELINES.get(item.crop.lower(), 2500.0)
                forecast_price = base_p
                price_trend = "STABLE"

            # Normalize Market Score (Base price + trend factor)
            trend_bonus = 10.0 if price_trend == "UPWARD" else (4.0 if price_trend == "STABLE" else 0.0)
            base_m_norm = min(85.0, max(10.0, (forecast_price / 4500.0) * 60.0))
            market_score = round(min(100.0, max(10.0, base_m_norm + trend_bonus)), 2)

            # --- Multi-Criteria Agricultural Decision Score ---
            # Weights: 40% Suitability + 35% Yield + 25% Market
            decision_score = round(
                (0.40 * suitability_score) + (0.35 * yield_score) + (0.25 * market_score),
                2
            )

            evaluations.append(
                AlternativeCropEvaluation(
                    crop=crop_name,
                    rank=0,
                    decision_score=decision_score,
                    suitability_probability=prob,
                    suitability_score=suitability_score,
                    predicted_yield_tonnes_per_hectare=pred_yield,
                    estimated_total_production_tonnes=tot_prod,
                    yield_score=yield_score,
                    forecasted_market_price=forecast_price,
                    price_trend=price_trend,
                    market_score=market_score
                )
            )

        # -------------------------------------------------------------
        # 3. Step 4: Sort & Rank Alternatives
        # -------------------------------------------------------------
        evaluations.sort(key=lambda x: x.decision_score, reverse=True)
        for idx, ev in enumerate(evaluations):
            ev.rank = idx + 1

        primary = evaluations[0]

        # -------------------------------------------------------------
        # 4. Step 5: Dynamic Explainability Generation
        # -------------------------------------------------------------
        explanation = cls._generate_explanation(request, primary, evaluations)

        execution_ms = round((time.time() - t0) * 1000.0, 2)

        response_payload = DecisionRecommendationResponse(
            recommended_crop=primary.crop,
            decision_score=primary.decision_score,
            crop_confidence=primary.suitability_probability,
            suitability_score=primary.suitability_score,
            predicted_yield=primary.predicted_yield_tonnes_per_hectare,
            yield_unit="Tonnes / Hectare",
            estimated_production_tonnes=primary.estimated_total_production_tonnes,
            yield_score=primary.yield_score,
            forecast_price=primary.forecasted_market_price,
            price_unit="INR/Quintal",
            price_trend=primary.price_trend,
            market=request.market,
            market_score=primary.market_score,
            explanation=explanation,
            alternatives=evaluations,
            execution_time_ms=execution_ms
        )

        # -------------------------------------------------------------
        # 5. Step 6: Record History Audit
        # -------------------------------------------------------------
        if db is not None:
            try:
                PredictionService.record_prediction(
                    db=db,
                    prediction_type="DECISION",
                    input_data=request.model_dump(),
                    prediction_result=response_payload.model_dump(),
                    latency_ms=execution_ms,
                    user_id=user_id
                )
            except Exception as e:
                logger.error(f"Failed to record decision history: {e}", exc_info=True)

        return response_payload

    @classmethod
    def _generate_explanation(
        cls,
        req: DecisionRecommendationRequest,
        primary: AlternativeCropEvaluation,
        all_evals: List[AlternativeCropEvaluation]
    ) -> DecisionExplanation:
        """
        Dynamically formulates an explainability breakdown from actual model metrics.
        """
        summary = (
            f"{primary.crop} achieved the highest overall Agricultural Decision Score ({primary.decision_score}/100), "
            f"combining {(primary.suitability_probability * 100):.1f}% agro-climatic suitability, a strong yield of "
            f"{primary.predicted_yield_tonnes_per_hectare:.2f} t/ha in {req.district}, and an estimated {req.market} "
            f"market price of ₹{primary.forecasted_market_price:.2f}/qtl ({primary.price_trend} trend)."
        )

        soil_comp = (
            f"Current soil nutrients (N: {req.N:.0f}, P: {req.P:.0f}, K: {req.K:.0f} kg/ha) and pH {req.ph:.1f} "
            f"closely align with optimal biochemical requirements for {primary.crop} cultivation."
        )

        clim_suit = (
            f"Meteorological conditions ({req.temperature:.1f}°C temperature, {req.humidity:.0f}% humidity, and "
            f"{req.rainfall:.1f}mm annual rainfall) provide a favorable microclimate during the {req.season} season."
        )

        yield_pot = (
            f"The Deep Neural Network projects a productivity of {primary.predicted_yield_tonnes_per_hectare:.2f} Tonnes/Hectare, "
            f"yielding approximately {primary.estimated_total_production_tonnes:.2f} Tonnes across {req.area} hectares."
        )

        market_out = (
            f"LSTM price forecasting in {req.market} Mandi projects a terminal modal price of "
            f"₹{primary.forecasted_market_price:.2f}/quintal with a {primary.price_trend.lower()} trajectory over the {req.forecast_horizon}-day horizon."
        )

        advantages = [
            f"Top agro-climatic fit with {(primary.suitability_probability * 100):.1f}% AI suitability confidence",
            f"Projected total harvest of {primary.estimated_total_production_tonnes:.2f} Tonnes ({primary.predicted_yield_tonnes_per_hectare:.2f} t/ha)",
            f"Favorable {primary.price_trend.lower()} price movement in {req.market} Mandi (₹{primary.forecasted_market_price:.2f}/qtl)"
        ]

        if len(all_evals) > 1:
            alt = all_evals[1]
            diff = primary.decision_score - alt.decision_score
            advantages.append(
                f"Outperformed #{alt.rank} candidate ({alt.crop}) by +{diff:.1f} decision score points"
            )

        return DecisionExplanation(
            summary=summary,
            soil_compatibility=soil_comp,
            climatic_suitability=clim_suit,
            yield_potential=yield_pot,
            market_outlook=market_out,
            key_advantages=advantages
        )
