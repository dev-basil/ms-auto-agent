import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule],
  template: `
    <header class="header">
      <div class="logo">
        <h1>Auto-Agent Admin</h1>
      </div>
      <div class="user-profile">
        <span class="username">Admin User</span>
        <div class="avatar">
           <svg xmlns="http://www.w3.org/2000/svg" height="24" viewBox="0 -960 960 960" width="24" fill="#fff"><path d="M480-480q-66 0-113-47t-47-113q0-66 47-113t113-47q66 0 113 47t47 113q0 66-47 113t-113 47ZM160-160v-32q0-34 17.5-62.5T224-306q54-27 109-41.5T480-362q57 0 112 14.5t109 41.5q32 26 49.5 54.5T768-192v32H160Zm80-80h480v-32q0-11-5.5-20T700-306q-54-27-109-41.5T480-362q-56 0-111 14.5T260-306q-9 5-14.5 14t-5.5 20v32Zm240-320q33 0 56.5-23.5T560-640q0-33-23.5-56.5T480-720q-33 0-56.5 23.5T400-640q0 33 23.5 56.5T480-560Zm0-80Zm0 400Z"/></svg>
        </div>
      </div>
    </header>
  `,
  styles: [`
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.5rem 1.5rem;
      background-color: #1f2937;
      color: white;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      height: 60px;
    }
    .logo h1 {
      font-size: 1.25rem;
      font-weight: 600;
      margin: 0;
      color: #60a5fa;
    }
    .user-profile {
      display: flex;
      align-items: center;
      gap: 1rem;
    }
    .username {
      font-size: 0.875rem;
      color: #e5e7eb;
    }
    .avatar {
      width: 36px;
      height: 36px;
      background-color: #3b82f6;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
    }
  `]
})
export class HeaderComponent { }
