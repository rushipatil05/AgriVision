import { Component, input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-empty-state',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './empty-state.component.html',
  styleUrl: './empty-state.component.css'
})
export class EmptyStateComponent {
  public title = input<string>('No Records Found');
  public message = input<string>('There are no predictions or items available at this time.');
  public icon = input<string>('inbox');
}
