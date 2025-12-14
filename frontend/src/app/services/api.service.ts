import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, Subject } from 'rxjs';
import { map } from 'rxjs/operators';

export interface Action {
  id: string;
  text: string;
  count: number;
  timestamp: number;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:8000/api';
  private wsUrl = 'ws://localhost:8000/ws';

  private logsSubject = new Subject<string>();
  public logs$ = this.logsSubject.asObservable();

  private actionsSubject = new Subject<Action[]>();
  public actions$ = this.actionsSubject.asObservable();

  constructor(private http: HttpClient) {
    this.connectLogStream();
    this.connectActionStream();
  }

  private connectLogStream() {
    const ws = new WebSocket(`${this.wsUrl}/logs`);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.logs) {
          this.logsSubject.next(data.logs);
        }
      } catch (e) {
        console.error('Error parsing log message', e);
      }
    };
    ws.onclose = () => {
      setTimeout(() => this.connectLogStream(), 3000);
    };
  }

  private connectActionStream() {
    const ws = new WebSocket(`${this.wsUrl}/actions`);
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (Array.isArray(data)) {
          // Sort by latest first
          data.sort((a, b) => b.timestamp - a.timestamp);
          this.actionsSubject.next(data);
        }
      } catch (e) {
        console.error('Error parsing action message', e);
      }
    };
    ws.onclose = () => {
      setTimeout(() => this.connectActionStream(), 3000);
    };
  }

  approveAction(id: string) {
    return this.http.post(`${this.apiUrl}/actions/${id}/approve`, {});
  }

  rejectAction(id: string) {
    return this.http.post(`${this.apiUrl}/actions/${id}/reject`, {});
  }
}
