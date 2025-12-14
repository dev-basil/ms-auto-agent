import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService, Action } from '../../services/api.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-action-list',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="action-container">
      <div class="action-header">
        <h2>Recommended Actions</h2>
        <span class="count-badge" *ngIf="actions.length > 0">{{ actions.length }} pending</span>
      </div>
      <div class="action-list">
        <div *ngIf="actions.length === 0" class="empty-state">
           <svg xmlns="http://www.w3.org/2000/svg" height="48" viewBox="0 -960 960 960" width="48" fill="#30363d"><path d="M382-240 154-468l57-57 171 171 367-367 57 57-424 424Z"/></svg>
           <p>All clear! No errors detected.</p>
        </div>

        <div class="action-card" *ngFor="let action of actions">
          <div class="card-header">
            <span class="alert-icon">⚠️</span>
            <span class="timestamp">{{ action.timestamp * 1000 | date:'shortTime' }}</span>
          </div>
          <div class="card-content">
            <p>{{ action.text }}</p>
          </div>
          <div class="card-footer">
            <div class="count-pill" *ngIf="action.count > 1">
              Occurred {{ action.count }} times
            </div>
            <div class="actions">
              <button class="btn-reject" (click)="onReject(action.id)">Reject</button>
              <button class="btn-approve" (click)="onApprove(action.id)">Approve</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .action-container {
      display: flex;
      flex-direction: column;
      height: 100%;
      background-color: #f6f8fa;
    }
    .action-header {
      padding: 1rem;
      background-color: #ffffff;
      border-bottom: 1px solid #d0d7de;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .action-header h2 {
      margin: 0;
      font-size: 1rem;
      color: #24292f;
    }
    .count-badge {
      background-color: #cf222e;
      color: white;
      padding: 2px 8px;
      font-size: 0.75rem;
      border-radius: 12px;
      font-weight: 600;
    }
    .action-list {
      flex: 1;
      padding: 1rem;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100%;
      color: #57606a;
    }
    .action-card {
      background: white;
      border: 1px solid #d0d7de;
      border-radius: 6px;
      padding: 1rem;
      box-shadow: 0 1px 3px rgba(0,0,0,0.04);
      transition: transform 0.2s;
    }
    .action-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .card-header {
      display: flex;
      justify-content: space-between;
      margin-bottom: 0.5rem;
      color: #57606a;
      font-size: 0.85rem;
    }
    .card-content p {
      margin: 0;
      color: #1f2328;
      font-weight: 500;
      line-height: 1.5;
    }
    .card-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 1rem;
    }
    .count-pill {
      background-color: #ddf4ff;
      color: #0969da;
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 0.75rem;
      font-weight: 500;
    }
    .actions {
      display: flex;
      gap: 0.5rem;
      margin-left: auto;
    }
    button {
      border: none;
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 0.875rem;
      cursor: pointer;
      font-weight: 500;
      transition: background-color 0.2s;
    }
    .btn-reject {
      background-color: #f6f8fa;
      color: #cf222e;
      border: 1px solid #d0d7de;
    }
    .btn-reject:hover {
      background-color: #f3f4f6;
    }
    .btn-approve {
      background-color: #1f883d;
      color: white;
    }
    .btn-approve:hover {
      background-color: #1a7f37;
    }
  `]
})
export class ActionListComponent implements OnInit, OnDestroy {
  actions: Action[] = [];
  sub!: Subscription;

  constructor(private api: ApiService) { }

  ngOnInit() {
    this.sub = this.api.actions$.subscribe(actions => {
      this.actions = actions;
    });
  }

  onApprove(id: string) {
    this.api.approveAction(id).subscribe();
  }

  onReject(id: string) {
    this.api.rejectAction(id).subscribe();
  }

  ngOnDestroy() {
    if (this.sub) this.sub.unsubscribe();
  }
}
