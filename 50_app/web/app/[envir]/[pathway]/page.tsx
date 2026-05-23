"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

/**
 * Per-envir + per-pathway lesson list. Per F-055 axis #6 + D-070.
 *
 * Fetches the lesson catalog from the FastAPI bridge at port 8000.
 * Production deployment serves both UI + API behind the same origin.
 */

interface LessonSummary {
  lesson_id: string;
  title_en: string;
  title_es: string;
  title_cab: string | null;
  unit_count: number;
  estimated_minutes: number;
}

interface LessonListResponse {
  envir: string;
  pathway: string;
  lessons: LessonSummary[];
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function EnvirPathwayPage() {
  const params = useParams<{ envir: string; pathway: string }>();
  const envir = params.envir;
  const pathway = params.pathway;
  const [data, setData] = useState<LessonListResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!envir || !pathway) return;
    fetch(`${API_BASE}/api/v1/envir/${envir}/pathway/${pathway}/lessons`)
      .then((r) => {
        if (!r.ok) throw new Error(`API ${r.status}`);
        return r.json();
      })
      .then(setData)
      .catch((e) => setError(String(e)));
  }, [envir, pathway]);

  return (
    <main id="main-content" className="mx-auto max-w-3xl px-4 py-8">
      <header className="mb-6">
        <h1 className="text-3xl font-bold capitalize">
          {pathway} path — {envir.replace(/_/g, " ")}
        </h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Lessons curated for your community + pathway. Per <em>Labayayahoun Ibagari</em>:
          each lesson cites attribution back to source.
        </p>
      </header>

      {error && (
        <div className="rounded-md border border-red-300 bg-red-50/40 p-3 text-sm dark:border-red-700 dark:bg-red-950/30">
          Failed to load lessons: {error}.
          <br />
          <span className="text-xs">
            Is the FastAPI bridge running?{" "}
            <code>cd 50_app/api && uvicorn main:app --port 8000</code>
          </span>
        </div>
      )}

      {!data && !error && (
        <div className="text-muted-foreground">Loading lessons...</div>
      )}

      {data && (
        <ol className="space-y-3">
          {data.lessons.map((lesson) => (
            <li
              key={lesson.lesson_id}
              className="rounded-lg border bg-card p-4 transition hover:shadow-md"
            >
              <Link
                href={`/${envir}/${pathway}/lesson/${lesson.lesson_id}`}
                className="block"
              >
                <h2 className="text-lg font-semibold">{lesson.title_en}</h2>
                {lesson.title_cab && (
                  <div className="text-sm font-medium text-primary">
                    {lesson.title_cab}
                  </div>
                )}
                <div className="text-sm text-muted-foreground">{lesson.title_es}</div>
                <div className="mt-2 text-xs text-muted-foreground">
                  {lesson.unit_count} units · ~{lesson.estimated_minutes} min
                </div>
              </Link>
            </li>
          ))}
        </ol>
      )}
    </main>
  );
}
