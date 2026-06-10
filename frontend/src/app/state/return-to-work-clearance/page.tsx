import { redirect } from "next/navigation";

export default function Page() {
  redirect("/state/reports?category=return_to_work");
}
