import { redirect } from "next/navigation";

export default function Page() {
  redirect("/state/directory?tab=food-handlers");
}
