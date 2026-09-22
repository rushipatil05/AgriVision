import { Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-stat-card',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './stat-card.component.html',
  styleUrl: './stat-card.component.css'
})
export class StatCardComponent {
  public title = input.required<string>();
  public value = input.required<string | number>();
  public subtitle = input<string>('');
  public icon = input<string>('analytics');
  public trend = input<string>('');
  public color = input<'emerald' | 'teal' | 'amber' | 'blue' | 'purple'>('emerald');
}
