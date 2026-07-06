/**
 * Warm-up ping: /api/warmup → backend/ (root health endpoint)
 *
 * Why this exists: on Render's free plan, frontend and backend are two
 * independent web services that spin down after inactivity and wake up
 * independently — there is no "start frontend, backend follows" on free
 * tier. Without this, a user's first questionnaire submit hits a cold
 * backend and can time out (30-60s+ cold start).
 *
 * This route is called fire-and-forget from the root layout on every page
 * load, so the backend is already waking up by the time the user reaches
 * the assess form. It does NOT block rendering and never throws to the
 * caller — a failed/slow warm-up ping should never break the page.
 */
import { NextResponse } from 'next/server';

const BACKEND = (process.env.BACKEND_URL ?? 'http://backend:8000').replace(/\/$/, '');

export async function GET() {
  try {
    const res = await fetch(BACKEND, {
      method: 'GET',
      signal: AbortSignal.timeout(5_000),
      cache: 'no-store',
    });
    return NextResponse.json({ warmed: res.ok }, { status: 200 });
  } catch {
    // Backend is cold-starting or unreachable — that's expected, not an error.
    // Report warmed:false so the client can decide to retry, but always 200.
    return NextResponse.json({ warmed: false }, { status: 200 });
  }
}
