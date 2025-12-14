import { Component, ElementRef, OnInit, ViewChild, AfterViewChecked, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-log-stream',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="log-container">
      <div class="log-header">
        <h2>Live Logs</h2>
        <span class="status-badge">Streaming</span>
      </div>
      <div class="log-content" #logContainer>
        <pre *ngFor="let log of logs">{{ log }}</pre>
        <div *ngIf="logs.length === 0" class="empty-state">Waiting for logs...</div>
      </div>
    </div>
  `,
  styles: [`
    .log-container {
      display: flex;
      flex-direction: column;
      height: 100%;
      background-color: #0d1117;
      border-right: 1px solid #30363d;
      overflow: hidden;
    }
    .log-header {
      padding: 1rem;
      border-bottom: 1px solid #30363d;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background-color: #161b22;
    }
    .log-header h2 {
      color: #e6edf3;
      margin: 0;
      font-size: 1rem;
    }
    .status-badge {
      font-size: 0.75rem;
      background-color: #238636;
      color: white;
      padding: 2px 8px;
      border-radius: 12px;
    }
    .log-content {
      flex: 1;
      overflow-y: auto;
      padding: 1rem;
      font-family: 'JetBrains Mono', 'Fira Code', monospace;
      font-size: 0.825rem;
      color: #c9d1d9;
      white-space: pre-wrap;
    }
    pre {
      margin: 0;
      line-height: 1.4;
    }
    .empty-state {
      color: #8b949e;
      text-align: center;
      margin-top: 2rem;
      font-style: italic;
    }
    /* Scrollbar styling */
    .log-content::-webkit-scrollbar {
      width: 8px;
    }
    .log-content::-webkit-scrollbar-track {
      background: #0d1117;
    }
    .log-content::-webkit-scrollbar-thumb {
      background: #30363d;
      border-radius: 4px;
    }
  `]
})
export class LogStreamComponent implements OnInit, OnDestroy, AfterViewChecked {
  logs: string[] = [];
  private sub!: Subscription;
  @ViewChild('logContainer') private logContainer!: ElementRef;

  constructor(private apiService: ApiService) { }

  ngOnInit() {
    this.sub = this.apiService.logs$.subscribe(logChunk => {
      // Split chunk by newlines and append
      const lines = logChunk.split('\n');
      this.logs.push(...lines);
      // Keep buffer size reasonable if needed
      if (this.logs.length > 5000) {
        this.logs = this.logs.slice(this.logs.length - 5000);
      }
    });
  }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  scrollToBottom(): void {
    try {
      this.logContainer.nativeElement.scrollTop = this.logContainer.nativeElement.scrollHeight;
    } catch (err) { }
  }

  ngOnDestroy() {
    if (this.sub) this.sub.unsubscribe();
  }
}
