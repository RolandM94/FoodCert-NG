"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function Page() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/state/certificates?tab=pending_review");
  }, [router]);

  return <p className="p-6 text-sm text-neutral-500">Opening certificate registry...</p>;
}
