import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { z } from "zod";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import {
  scheduleFlight,
  delayFlight,
  launchFlight,
  landFlight,
  cancelFlight,
  replaceAircraft,
  scheduleFlightCrew
} from "@/api/flight";
import { listRoutes } from "@/api/routes";
import { getAllAircraft } from "@/api/resources";
import { Card, CardContent, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { FieldError, Input, Label, Textarea } from "@/components/ui/Field";
import { Badge } from "@/components/ui/Badge";
import { readJson, writeJson } from "@/lib/storage";
import type { FlightRead } from "@/types/flight";
import { fmtDateTime } from "@/lib/date";

const RECENT_FLIGHTS_KEY = "ao.recentFlights.v1";

function formatFlightName(flightId?: string) {
  if (!flightId) {
    return "—";
  }
  return `FL-${flightId.slice(0, 8).toUpperCase()}`;
}

function formatAircraftName(manufacturer?: string, aircraftModel?: string) {
  const make = (manufacturer ?? "").trim();
  const model = (aircraftModel ?? "").trim();
  if (make && model) {
    return `${make} ${model}`;
  }
  if (make) {
    return make;
  }
  if (model) {
    return model;
  }
  return "Unknown aircraft";
}

function upsertRecent(flight: FlightRead) {
  const existing = readJson<FlightRead[]>(RECENT_FLIGHTS_KEY, []);
  const next = [flight, ...existing.filter((f) => f.flight_id !== flight.flight_id)].slice(0, 50);
  writeJson(RECENT_FLIGHTS_KEY, next);
}

function markRecentFlightArrived(flightId: string) {
  const existing = readJson<FlightRead[]>(RECENT_FLIGHTS_KEY, []);
  const next = existing.map((f) =>
    f.flight_id === flightId
      ? { ...f, flight_status: "ARRIVED", arrival_time: new Date().toISOString() }
      : f
  );
  writeJson(RECENT_FLIGHTS_KEY, next);
}


function statusTone(status?: string) {
  switch (status) {
    case "ARRIVED":
      return "ok";
    case "IN-FLIGHT":
    case "SCHEDULED":
      return "info";
    case "DELAYED":
      return "warn";
    case "CANCELLED":
      return "bad";
    default:
      return "neutral";
  }
}

const ScheduleSchema = z.object({
  route_id: z.string().min(1),
  aircraft_id: z.string().min(1),
  departure_time: z.string().min(1),
  arrival_time: z.string().min(1)
});

const DelaySchema = z.object({
  flight_id: z.string().min(1),
  extra_minutes: z.coerce.number().int().positive()
});

const FlightIdSchema = z.object({
  flight_id: z.string().min(1)
});

const ReplaceSchema = z.object({
  flight_id: z.string().min(1),
  aircraft_id: z.string().min(1)
});

const CrewSchema = z.object({
  flight_id: z.string().min(1),
  employee_ids: z.string().min(1, "Provide at least one employee UUID")
});

export default function FlightOpsPage() {
  const [lastResult, setLastResult] = useState<unknown>(null);
  const [viewTab, setViewTab] = useState<"ops" | "ops_result">("ops");
  const routesQ = useQuery({ queryKey: ["routes", "all"], queryFn: listRoutes });
  const aircraftQ = useQuery({ queryKey: ["aircraft", "all"], queryFn: getAllAircraft });

  const scheduleForm = useForm<z.infer<typeof ScheduleSchema>>({
    resolver: zodResolver(ScheduleSchema),
    defaultValues: { route_id: "", aircraft_id: "", departure_time: "", arrival_time: "" }
  });

  const delayForm = useForm<z.infer<typeof DelaySchema>>({
    resolver: zodResolver(DelaySchema),
    defaultValues: { flight_id: "", extra_minutes: 15 }
  });

  const flightIdForm = useForm<z.infer<typeof FlightIdSchema>>({
    resolver: zodResolver(FlightIdSchema),
    defaultValues: { flight_id: "" }
  });

  const replaceForm = useForm<z.infer<typeof ReplaceSchema>>({
    resolver: zodResolver(ReplaceSchema),
    defaultValues: { flight_id: "", aircraft_id: "" }
  });

  const crewForm = useForm<{ flight_id: string; employee_ids: string }>({
    resolver: zodResolver(CrewSchema),
    defaultValues: { flight_id: "", employee_ids: "" }
  });

  const scheduleMut = useMutation({
    mutationFn: (v: z.infer<typeof ScheduleSchema>) => scheduleFlight(v),
    onSuccess: (data) => {
      upsertRecent(data as any);
      setLastResult(data);
      toast.success("Flight scheduled ✅");
      scheduleForm.reset();
    }
  });

  const delayMut = useMutation({
    mutationFn: (v: z.infer<typeof DelaySchema>) => delayFlight(v),
    onSuccess: (data) => {
      upsertRecent(data as any);
      setLastResult(data);
      toast.success("Delay applied ⏱️");
    }
  });

  const launchMut = useMutation({
    mutationFn: (v: z.infer<typeof FlightIdSchema>) => launchFlight(v),
    onSuccess: (data) => {
      upsertRecent(data as any);
      setLastResult(data);
      toast.success("Flight launched ✈️");
    }
  });

  const landMut = useMutation({
    mutationFn: (v: z.infer<typeof FlightIdSchema>) => landFlight(v),
    onSuccess: (data, variables) => {
      if (variables?.flight_id) {
        markRecentFlightArrived(variables.flight_id);
      }
      setLastResult(data);
      toast.success("Landing confirmed 🛬");
    }
  });

  const cancelMut = useMutation({
    mutationFn: (v: z.infer<typeof FlightIdSchema>) => cancelFlight(v),
    onSuccess: (data) => {
      upsertRecent(data as any);
      setLastResult(data);
      toast.success("Flight cancelled 🧾");
    }
  });

  const replaceMut = useMutation({
    mutationFn: (v: z.infer<typeof ReplaceSchema>) => replaceAircraft(v),
    onSuccess: (data) => {
      upsertRecent(data as any);
      setLastResult(data);
      toast.success("Aircraft replaced 🔁");
    }
  });

  const crewMut = useMutation({
    mutationFn: (v: { flight_id: string; employee_ids: string }) =>
      scheduleFlightCrew({ flight_id: v.flight_id, employee_ids: v.employee_ids.split(",").map((x) => x.trim()).filter(Boolean) }),
    onSuccess: (data) => {
      setLastResult(data);
      toast.success("Crew scheduled 👥");
      crewForm.reset();
    }
  });

  const loadingAny =
    scheduleMut.isPending ||
    delayMut.isPending ||
    launchMut.isPending ||
    landMut.isPending ||
    cancelMut.isPending ||
    replaceMut.isPending ||
    crewMut.isPending;

  const recent = readJson<FlightRead[]>(RECENT_FLIGHTS_KEY, []);
  const latest = useMemo(() => recent[0], [recent]);
  const routeLabelById = useMemo(() => {
    const routes = routesQ.data ?? [];
    return new Map(
      routes.map((route) => [route.route_id, `${route.origin_airport_code} → ${route.destination_airport_code}`])
    );
  }, [routesQ.data]);
  const aircraftLabelById = useMemo(() => {
    const aircraftList = aircraftQ.data ?? [];
    return new Map(
      aircraftList.map((aircraft) => [
        aircraft.aircraft_id,
        formatAircraftName(aircraft.manufacturer, aircraft.aircraft_model)
      ])
    );
  }, [aircraftQ.data]);

  return (
    <div className="space-y-6">
      <div>
        <div className="text-xl font-semibold">Flight Operations</div>
        <div className="mt-1 text-sm text-zinc-400">
          Schedule and control flights. Use /flight/all for complete flight listings and this page for direct ops actions by ID.
        </div>
      </div>

      <div className="inline-flex rounded-xl border border-white/10 bg-zinc-900/60 p-1">
        <Button
          type="button"
          size="sm"
          variant={viewTab === "ops" ? "secondary" : "ghost"}
          onClick={() => setViewTab("ops")}
        >
          Operations only
        </Button>
        <Button
          type="button"
          size="sm"
          variant={viewTab === "ops_result" ? "secondary" : "ghost"}
          onClick={() => setViewTab("ops_result")}
        >
          Operations + API result
        </Button>
      </div>

      {latest && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between gap-3">
              <div>
                <div className="text-sm font-semibold">Latest flight touched</div>
                <div className="mt-1 text-xs font-semibold text-zinc-100">{formatFlightName(latest.flight_id)}</div>
                <div className="text-xs text-zinc-500 font-mono">{latest.flight_id}</div>
              </div>
              <Badge tone={statusTone(latest.flight_status) as any}>{latest.flight_status ?? "UNKNOWN"}</Badge>
            </div>
          </CardHeader>
          <CardContent className="grid gap-3 md:grid-cols-4">
            <div>
              <div className="text-xs text-zinc-500">Route</div>
              <div className="mt-1 text-xs font-semibold text-zinc-100">
                {latest.route_id ? routeLabelById.get(latest.route_id) ?? "Unknown route" : "—"}
              </div>
              <div className="font-mono text-xs text-zinc-400">{latest.route_id ?? "—"}</div>
            </div>
            <div>
              <div className="text-xs text-zinc-500">Aircraft</div>
              <div className="mt-1 text-xs font-semibold text-zinc-100">
                {latest.aircraft_id ? aircraftLabelById.get(latest.aircraft_id) ?? "Unknown aircraft" : "—"}
              </div>
              <div className="font-mono text-xs text-zinc-400">{latest.aircraft_id ?? "—"}</div>
            </div>
            <div>
              <div className="text-xs text-zinc-500">Departure</div>
              <div className="mt-1 text-xs">{fmtDateTime(latest.departure_time)}</div>
            </div>
            <div>
              <div className="text-xs text-zinc-500">Arrival</div>
              <div className="mt-1 text-xs">{fmtDateTime(latest.arrival_time)}</div>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <div className="text-sm font-semibold">Schedule flight</div>
            <div className="text-xs text-zinc-500">POST /flight/schedule/</div>
          </CardHeader>
          <CardContent>
            <form
              className="grid gap-3"
              onSubmit={scheduleForm.handleSubmit((v) => scheduleMut.mutate(v))}
            >
              <div>
                <Label>Route ID (UUID)</Label>
                <Input placeholder="route_id" {...scheduleForm.register("route_id")} />
                <FieldError>{scheduleForm.formState.errors.route_id?.message}</FieldError>
              </div>
              <div>
                <Label>Aircraft ID (UUID)</Label>
                <Input placeholder="aircraft_id" {...scheduleForm.register("aircraft_id")} />
                <FieldError>{scheduleForm.formState.errors.aircraft_id?.message}</FieldError>
              </div>
              <div className="grid gap-3 md:grid-cols-2">
                <div>
                  <Label>Departure time (ISO)</Label>
                  <Input placeholder="2026-02-17T14:00:00" {...scheduleForm.register("departure_time")} />
                  <FieldError>{scheduleForm.formState.errors.departure_time?.message}</FieldError>
                </div>
                <div>
                  <Label>Arrival time (ISO)</Label>
                  <Input placeholder="2026-02-17T16:00:00" {...scheduleForm.register("arrival_time")} />
                  <FieldError>{scheduleForm.formState.errors.arrival_time?.message}</FieldError>
                </div>
              </div>
              <Button disabled={loadingAny} type="submit">
                {scheduleMut.isPending ? "Scheduling…" : "Schedule"}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="text-sm font-semibold">Delay flight</div>
            <div className="text-xs text-zinc-500">PATCH /flight/delay/</div>
          </CardHeader>
          <CardContent>
            <form className="grid gap-3" onSubmit={delayForm.handleSubmit((v) => delayMut.mutate(v))}>
              <div>
                <Label>Flight ID (UUID)</Label>
                <Input placeholder="flight_id" {...delayForm.register("flight_id")} />
                <FieldError>{delayForm.formState.errors.flight_id?.message}</FieldError>
              </div>
              <div>
                <Label>Extra minutes</Label>
                <Input type="number" {...delayForm.register("extra_minutes")} />
                <FieldError>{delayForm.formState.errors.extra_minutes?.message}</FieldError>
              </div>
              <Button disabled={loadingAny} type="submit" variant="secondary">
                {delayMut.isPending ? "Applying…" : "Apply delay"}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="text-sm font-semibold">Launch / Land / Cancel</div>
            <div className="text-xs text-zinc-500">PATCH /flight/launch/ • /flight/land/ • /flight/cancel</div>
          </CardHeader>
          <CardContent>
            <form className="grid gap-3" onSubmit={flightIdForm.handleSubmit((v) => launchMut.mutate(v))}>
              <div>
                <Label>Flight ID (UUID)</Label>
                <Input placeholder="flight_id" {...flightIdForm.register("flight_id")} />
                <FieldError>{flightIdForm.formState.errors.flight_id?.message}</FieldError>
              </div>
              <div className="flex flex-wrap gap-2">
                <Button disabled={loadingAny} type="submit">
                  {launchMut.isPending ? "Launching…" : "Launch"}
                </Button>
                <Button
                  disabled={loadingAny}
                  type="button"
                  variant="secondary"
                  onClick={() => landMut.mutate(flightIdForm.getValues())}
                >
                  {landMut.isPending ? "Landing…" : "Land"}
                </Button>
                <Button
                  disabled={loadingAny}
                  type="button"
                  variant="danger"
                  onClick={() => cancelMut.mutate(flightIdForm.getValues())}
                >
                  {cancelMut.isPending ? "Cancelling…" : "Cancel"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="text-sm font-semibold">Replace aircraft</div>
            <div className="text-xs text-zinc-500">PATCH /flight/replace/</div>
          </CardHeader>
          <CardContent>
            <form className="grid gap-3" onSubmit={replaceForm.handleSubmit((v) => replaceMut.mutate(v))}>
              <div>
                <Label>Flight ID (UUID)</Label>
                <Input placeholder="flight_id" {...replaceForm.register("flight_id")} />
                <FieldError>{replaceForm.formState.errors.flight_id?.message}</FieldError>
              </div>
              <div>
                <Label>New aircraft ID (UUID)</Label>
                <Input placeholder="aircraft_id" {...replaceForm.register("aircraft_id")} />
                <FieldError>{replaceForm.formState.errors.aircraft_id?.message}</FieldError>
              </div>
              <Button disabled={loadingAny} type="submit" variant="secondary">
                {replaceMut.isPending ? "Replacing…" : "Replace"}
              </Button>
            </form>
          </CardContent>
        </Card>

        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="text-sm font-semibold">Schedule flight crew</div>
            <div className="text-xs text-zinc-500">POST /flight/crew</div>
          </CardHeader>
          <CardContent>
            <form className="grid gap-3" onSubmit={crewForm.handleSubmit((v) => crewMut.mutate(v))}>
              <div className="grid gap-3 md:grid-cols-2">
                <div>
                  <Label>Flight ID (UUID)</Label>
                  <Input placeholder="flight_id" {...crewForm.register("flight_id")} />
                  <FieldError>{crewForm.formState.errors.flight_id?.message}</FieldError>
                </div>
                <div>
                  <Label>Employee IDs (comma-separated UUIDs)</Label>
                  <Input placeholder="uuid1, uuid2, uuid3" {...crewForm.register("employee_ids")} />
                  <FieldError>{crewForm.formState.errors.employee_ids?.message}</FieldError>
                </div>
              </div>
              <Button disabled={loadingAny} type="submit">
                {crewMut.isPending ? "Scheduling…" : "Schedule crew"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>

      {viewTab === "ops_result" && (
        <Card>
          <CardHeader>
            <div className="text-sm font-semibold">Last API result</div>
          </CardHeader>
          <CardContent>
            <Textarea readOnly value={lastResult ? JSON.stringify(lastResult, null, 2) : ""} placeholder="No actions yet." />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
