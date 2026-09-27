import { describe, expect, it, vi } from "vitest";
import { AppConnectClient } from "./index";

const BASE_URL = "https://example.invalid";
const ACCESS_TOKEN = "user-access-token";

function makeFetchMock(data: unknown, opts: { status?: number; success?: boolean } = {}) {
  const status = opts.status ?? 200;
  const success = opts.success ?? true;
  // Params are unused in the mock body but must be typed to match `typeof
  // fetch`'s call signature so `fetchMock.mock.calls` below is typed as
  // [string, RequestInit] rather than [].
  return vi.fn((..._args: [string, RequestInit?]) => {
    void _args;
    return Promise.resolve({
      ok: status >= 200 && status < 300,
      status,
      statusText: "",
      json: async () => (success ? { success: true, data } : { success: false, error: data }),
    });
  });
}

function makeClient(fetchMock: ReturnType<typeof makeFetchMock>) {
  return new AppConnectClient({
    baseUrl: BASE_URL,
    clientId: "client-id",
    clientSecret: "client-secret",
    fetch: fetchMock as unknown as typeof fetch,
  });
}

describe("AppConnectClient defaults", () => {
  it("uses the public AppConnect origin when baseUrl is omitted", async () => {
    const fetchMock = makeFetchMock({ trigger_definitions: [] });
    const client = new AppConnectClient({
      clientId: "client-id",
      clientSecret: "client-secret",
      fetch: fetchMock as unknown as typeof fetch,
    });

    await client.listTriggerDefinitions(ACCESS_TOKEN);

    expect(fetchMock).toHaveBeenCalledWith(
      "https://www.appconnecthq.com/api/trigger-definitions",
      expect.objectContaining({ method: "GET" }),
    );
  });
});

describe("AppConnectClient trigger methods", () => {
  it("listTriggerDefinitions hits GET /api/trigger-definitions with no query when service is omitted", async () => {
    const fetchMock = makeFetchMock({ trigger_definitions: [] });
    const client = makeClient(fetchMock);

    await client.listTriggerDefinitions(ACCESS_TOKEN);

    expect(fetchMock).toHaveBeenCalledWith(
      `${BASE_URL}/api/trigger-definitions`,
      expect.objectContaining({
        method: "GET",
        headers: expect.objectContaining({ Authorization: `Bearer ${ACCESS_TOKEN}` }),
      }),
    );
  });

  it("listTriggerDefinitions filters by service via querystring", async () => {
    const fixture = {
      trigger_definitions: [
        {
          id: "def_1",
          service: "github-oauth",
          serviceName: "GitHub",
          slug: "new_commit",
          displayName: "New Commit",
          description: null,
          mode: "webhook",
          configSchema: { type: "object" },
          payloadSchema: { type: "object" },
        },
      ],
    };
    const fetchMock = makeFetchMock(fixture);
    const client = makeClient(fetchMock);

    const result = await client.listTriggerDefinitions(ACCESS_TOKEN, "github-oauth");

    expect(fetchMock).toHaveBeenCalledWith(
      `${BASE_URL}/api/trigger-definitions?service=github-oauth`,
      expect.objectContaining({ method: "GET" }),
    );
    expect(result).toEqual(fixture);
  });

  it("subscribeTrigger POSTs to /api/triggers with snake_case callback_url", async () => {
    const fixture = {
      trigger: {
        id: "trg_1",
        service: "github-oauth",
        trigger: "new_commit",
        config: { owner: "octocat", repo: "hello-world" },
        callbackUrl: "https://partner.example.com/hooks/appconnect",
        status: "active",
        lastEventAt: null,
        lastPolledAt: null,
        errorMessage: null,
        createdAt: "2026-01-01T00:00:00.000Z",
        updatedAt: "2026-01-01T00:00:00.000Z",
      },
      signing_secret: "whsec_abc123",
    };
    const fetchMock = makeFetchMock(fixture);
    const client = makeClient(fetchMock);

    const result = await client.subscribeTrigger(ACCESS_TOKEN, {
      service: "github-oauth",
      trigger: "new_commit",
      config: { owner: "octocat", repo: "hello-world" },
      callbackUrl: "https://partner.example.com/hooks/appconnect",
    });

    expect(fetchMock).toHaveBeenCalledWith(
      `${BASE_URL}/api/triggers`,
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          service: "github-oauth",
          trigger: "new_commit",
          config: { owner: "octocat", repo: "hello-world" },
          callback_url: "https://partner.example.com/hooks/appconnect",
        }),
      }),
    );
    expect(result).toEqual(fixture);
  });

  it("listTriggerInstances hits GET /api/triggers", async () => {
    const fetchMock = makeFetchMock({ triggers: [] });
    const client = makeClient(fetchMock);

    await client.listTriggerInstances(ACCESS_TOKEN);

    expect(fetchMock).toHaveBeenCalledWith(
      `${BASE_URL}/api/triggers`,
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("getTriggerInstance hits GET /api/triggers/{id}", async () => {
    const fetchMock = makeFetchMock({ trigger: null });
    const client = makeClient(fetchMock);

    await client.getTriggerInstance(ACCESS_TOKEN, "trg_1");

    expect(fetchMock).toHaveBeenCalledWith(
      `${BASE_URL}/api/triggers/trg_1`,
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("updateTriggerInstance PATCHes /api/triggers/{id} and omits unset fields", async () => {
    const fetchMock = makeFetchMock({ trigger: null });
    const client = makeClient(fetchMock);

    await client.updateTriggerInstance(ACCESS_TOKEN, "trg_1", { status: "paused" });

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(init.method).toBe("PATCH");
    expect(JSON.parse(init.body as string)).toEqual({ status: "paused" });
  });

  it("updateTriggerInstance forwards callbackUrl and config when provided", async () => {
    const fetchMock = makeFetchMock({ trigger: null });
    const client = makeClient(fetchMock);

    await client.updateTriggerInstance(ACCESS_TOKEN, "trg_1", {
      callbackUrl: "https://partner.example.com/new-hook",
      config: { owner: "octocat", repo: "hello-world" },
    });

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(JSON.parse(init.body as string)).toEqual({
      callback_url: "https://partner.example.com/new-hook",
      config: { owner: "octocat", repo: "hello-world" },
    });
  });

  it("unsubscribeTrigger DELETEs /api/triggers/{id}", async () => {
    const fetchMock = makeFetchMock({ revoked: true });
    const client = makeClient(fetchMock);

    const result = await client.unsubscribeTrigger(ACCESS_TOKEN, "trg_1");

    expect(fetchMock).toHaveBeenCalledWith(
      `${BASE_URL}/api/triggers/trg_1`,
      expect.objectContaining({ method: "DELETE" }),
    );
    expect(result).toEqual({ revoked: true });
  });

  it("listDeliveries builds no querystring when opts are omitted", async () => {
    const fetchMock = makeFetchMock({ deliveries: [], nextCursor: null });
    const client = makeClient(fetchMock);

    await client.listDeliveries(ACCESS_TOKEN, "trg_1");

    expect(fetchMock).toHaveBeenCalledWith(
      `${BASE_URL}/api/triggers/trg_1/deliveries`,
      expect.objectContaining({ method: "GET" }),
    );
  });

  it("listDeliveries encodes status/limit/cursor into the querystring", async () => {
    const fetchMock = makeFetchMock({ deliveries: [], nextCursor: "2026-01-01T00:00:00.000Z" });
    const client = makeClient(fetchMock);

    await client.listDeliveries(ACCESS_TOKEN, "trg_1", {
      status: "failed",
      limit: 10,
      cursor: "2026-01-01T00:00:00.000Z",
    });

    const [url] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe(
      `${BASE_URL}/api/triggers/trg_1/deliveries?status=failed&limit=10&cursor=2026-01-01T00%3A00%3A00.000Z`,
    );
  });

  it("throws AppConnectError with the server error code on failure", async () => {
    const fetchMock = makeFetchMock(
      { message: "Trigger instance not found", code: "not_found" },
      { status: 404, success: false },
    );
    const client = makeClient(fetchMock);

    await expect(client.getTriggerInstance(ACCESS_TOKEN, "missing")).rejects.toMatchObject({
      status: 404,
      code: "not_found",
    });
  });
});
