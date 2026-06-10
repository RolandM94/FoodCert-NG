import { redirect } from "next/navigation";

export default function Page() {
  redirect("/employer/illness-reports?filter=return_to_work_pending");
}
