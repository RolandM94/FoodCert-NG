import { redirect } from "next/navigation";

export default function Page() {
  redirect("/state/reports?category=illness_exclusion");
}
