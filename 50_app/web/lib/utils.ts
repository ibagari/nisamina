import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * shadcn/ui canonical class-merge helper.
 * Combines clsx (conditional class composition) with tailwind-merge
 * (deduplicates Tailwind utility classes that conflict).
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
