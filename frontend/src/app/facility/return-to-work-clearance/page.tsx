import { redirect } from "next/navigation";

export default function Page() {
  redirect("/facility/assessments?queue=return-to-work");
}
