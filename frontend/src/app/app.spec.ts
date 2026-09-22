import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { App } from './app';

describe('App', () => {
  beforeEach(async () => {
    let store: Record<string, string> = {};
    if (typeof window !== 'undefined') {
      Object.defineProperty(window, 'localStorage', {
        value: {
          getItem: (key: string) => store[key] || null,
          setItem: (key: string, value: string) => { store[key] = value; },
          removeItem: (key: string) => { delete store[key]; },
          clear: () => { store = {}; }
        },
        writable: true
      });
    }

    await TestBed.configureTestingModule({
      imports: [App],
      providers: [
        provideRouter([]),
        provideHttpClient()
      ]
    }).compileComponents();
  });

  it('should create the app shell', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });

  it('should toggle sidebar status', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    expect(app.isSidebarOpen()).toBe(false);
    app.onToggleSidebar();
    expect(app.isSidebarOpen()).toBe(true);
    app.onCloseSidebar();
    expect(app.isSidebarOpen()).toBe(false);
  });
});
