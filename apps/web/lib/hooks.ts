"use client";

import { useEffect, useState } from "react";

export function useQueryParam(name: string): string | null {
  const [value, setValue] = useState<string | null>(null);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setValue(params.get(name));
  }, [name]);

  return value;
}

export function paperHref(id: number | string): string {
  return `/web/paper/?id=${id}`;
}

export function authorHref(id: number | string): string {
  return `/web/author/?id=${id}`;
}

export function institutionHref(id: number | string): string {
  return `/web/institution/?id=${id}`;
}
