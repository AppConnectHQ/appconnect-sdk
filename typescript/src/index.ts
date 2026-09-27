/**
 * The main entry point: `AppConnectClient`, its request and response types,
 * webhook signature verification, and the dependency-free OpenAI and
 * Anthropic tool adapters.
 *
 * @module sdk
 */
export * from "./framework";
export * from "./webhook-signature";

export const DEFAULT_BASE_URL = "https://www.appconnecthq.com";

export interface AppConnectClientOptions {
  baseUrl?: string;
  clientId: string;
  clientSecret: string;
  fetch?: typeof fetch;
}

export interface CreateLinkTokenParams {
  userId: string;
  redirectUri: string;
  state?: string;
  allowedServices?: string[];
  expiresIn?: number;
}

export interface CreateLinkTokenResponse {
  link_token: string;
  link_url: string;
  expires_at: string;
}

export interface PendingLinkExchangeResponse {
  status: "pending";
  user_id: string;
  state?: string | null;
  message: string;
}

export interface ConnectedLinkExchangeResponse {
  status: "connected";
  user_id: string;
  state?: string | null;
  access_token: string;
  refresh_token: string;
  token_type: "Bearer";
  expires_at: string;
  connected_services: string[];
}

export type ExchangeLinkTokenResponse = PendingLinkExchangeResponse | ConnectedLinkExchangeResponse;

export interface TokenResponse {
  access_token: string;
  token_type: "Bearer";
  expires_in: number;
  refresh_token: string;
  connected_services: string[];
}

export interface ToolExecutionResponse<T = unknown> {
  tool: string;
  data: T;
}

/**
 * A tool exposed by a connected service, as returned by GET /api/tools and
 * GET /api/tools/search. Mirrors the server's `listUserTools`
 * response shape.
 */
export interface AppConnectTool {
  /** Unified tool id, e.g. "google_calendar_list_events" — what executeTool expects. */
  id: string;
  /** Service slug, e.g. "google-calendar". */
  service: string;
  serviceName: string;
  /** Tool name within the service, e.g. "list_events". */
  name: string;
  displayName: string;
  description: string | null;
  method: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
  inputSchema: {
    type: string;
    properties?: Record<string, unknown>;
    required?: string[];
  } | null;
}

export interface ListToolsResponse {
  tools: AppConnectTool[];
}

export interface SearchToolsResponse {
  query: string;
  tools: AppConnectTool[];
}

/**
 * A trigger type available for a connected service, as returned by
 * GET /api/trigger-definitions. Mirrors the server's `listUserTriggerDefinitions`
 * response shape.
 */
export interface AppConnectTriggerDefinition {
  id: string;
  service: string;
  serviceName: string;
  /** Trigger type slug within the service, e.g. "new_commit". */
  slug: string;
  displayName: string;
  description: string | null;
  mode: "webhook" | "polling";
  /** JSON Schema describing what `subscribeTrigger`'s `config` must supply. */
  configSchema: unknown;
  /** JSON Schema documenting the normalized payload shape delivered to `callbackUrl`. */
  payloadSchema: unknown;
}

export interface ListTriggerDefinitionsResponse {
  trigger_definitions: AppConnectTriggerDefinition[];
}

/**
 * A subscription to a trigger for a connected account, as returned by
 * `api/triggers*`. Mirrors the server's `PublicTriggerInstance`
 * response shape.
 */
export interface AppConnectTriggerInstance {
  id: string;
  service: string;
  /** Trigger definition slug this instance subscribes to, e.g. "new_commit". */
  trigger: string;
  config: Record<string, unknown>;
  callbackUrl: string;
  status: string;
  lastEventAt: string | null;
  lastPolledAt: string | null;
  errorMessage: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface ListTriggerInstancesResponse {
  triggers: AppConnectTriggerInstance[];
}

export interface GetTriggerInstanceResponse {
  trigger: AppConnectTriggerInstance;
}

export interface SubscribeTriggerParams {
  service: string;
  trigger: string;
  config: Record<string, unknown>;
  callbackUrl: string;
}

export interface SubscribeTriggerResponse {
  trigger: AppConnectTriggerInstance;
  /**
   * Returned exactly once — store it yourself to verify
   * `X-AppConnect-Signature` on inbound deliveries via
   * `verifyWebhookSignature()`. Subsequent GETs never return it again.
   */
  signing_secret: string;
}

export interface UpdateTriggerInstanceParams {
  status?: "active" | "paused";
  callbackUrl?: string;
  config?: Record<string, unknown>;
}

export interface UpdateTriggerInstanceResponse {
  trigger: AppConnectTriggerInstance;
}

export interface UnsubscribeTriggerResponse {
  revoked: true;
}

/** One HTTP attempt at delivering an event to a trigger instance's `callbackUrl`. */
export interface AppConnectDeliveryAttempt {
  attemptNumber: number;
  statusCode: number | null;
  latencyMs: number | null;
  errorMessage: string | null;
  createdAt: string;
}

/**
 * A queued/delivered event row, as returned by
 * GET /api/triggers/{id}/deliveries. Mirrors the server's `PublicDelivery`
 * response shape.
 */
export interface AppConnectDelivery {
  id: string;
  eventId: string;
  eventType: string;
  status: string;
  attempts: number;
  maxAttempts: number;
  nextAttemptAt: string;
  lastAttemptAt: string | null;
  lastStatusCode: number | null;
  lastError: string | null;
  createdAt: string;
  updatedAt: string;
  latestAttempt: AppConnectDeliveryAttempt | null;
}

export interface ListDeliveriesOptions {
  status?: string;
  limit?: number;
  cursor?: string;
}

export interface ListDeliveriesResponse {
  deliveries: AppConnectDelivery[];
  nextCursor: string | null;
}

export class AppConnectError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = "AppConnectError";
    this.status = status;
    this.code = code;
  }
}

export class AppConnectClient {
  private readonly baseUrl: string;
  private readonly clientId: string;
  private readonly clientSecret: string;
  private readonly fetchImpl: typeof fetch;

  constructor(options: AppConnectClientOptions) {
    this.baseUrl = (options.baseUrl ?? DEFAULT_BASE_URL).replace(/\/$/, "");
    this.clientId = options.clientId;
    this.clientSecret = options.clientSecret;
    this.fetchImpl = options.fetch || fetch;
  }

  async createLinkToken(params: CreateLinkTokenParams) {
    return this.request<CreateLinkTokenResponse>("/api/link-tokens", {
      method: "POST",
      body: {
        client_id: this.clientId,
        client_secret: this.clientSecret,
        user_id: params.userId,
        redirect_uri: params.redirectUri,
        state: params.state,
        allowed_services: params.allowedServices,
        expires_in: params.expiresIn,
      },
    });
  }

  async exchangeLinkToken(linkToken: string) {
    return this.request<ExchangeLinkTokenResponse>("/api/link-tokens/exchange", {
      method: "POST",
      body: {
        client_id: this.clientId,
        client_secret: this.clientSecret,
        link_token: linkToken,
      },
    });
  }

  async exchangeAuthorizationCode(code: string, redirectUri: string) {
    return this.request<TokenResponse>("/api/oauth/token", {
      method: "POST",
      body: {
        grant_type: "authorization_code",
        code,
        client_id: this.clientId,
        client_secret: this.clientSecret,
        redirect_uri: redirectUri,
      },
    });
  }

  async refreshToken(refreshToken: string) {
    return this.request<TokenResponse>("/api/oauth/token", {
      method: "POST",
      body: {
        grant_type: "refresh_token",
        refresh_token: refreshToken,
        client_id: this.clientId,
        client_secret: this.clientSecret,
      },
    });
  }

  async listTools(accessToken: string) {
    return this.request<ListToolsResponse>("/api/tools", {
      method: "GET",
      accessToken,
    });
  }

  async searchTools(accessToken: string, query: string, limit?: number) {
    const params = new URLSearchParams({ q: query });
    if (limit !== undefined) {
      params.set("limit", String(limit));
    }

    return this.request<SearchToolsResponse>(`/api/tools/search?${params}`, {
      method: "GET",
      accessToken,
    });
  }

  async executeTool<T = unknown>(
    accessToken: string,
    tool: string,
    params: Record<string, unknown> = {},
  ) {
    return this.request<ToolExecutionResponse<T>>("/api/tools/execute", {
      method: "POST",
      accessToken,
      body: { tool, params },
    });
  }

  async proxy<T = unknown>(
    accessToken: string,
    service: string,
    path: string,
    init: Omit<RequestInit, "headers" | "body"> & { body?: unknown } = {},
  ) {
    const cleanPath = path.replace(/^\//, "");
    return this.request<T>(`/api/proxy/${service}/${cleanPath}`, {
      method: init.method || "GET",
      accessToken,
      body: init.body,
    });
  }

  /**
   * GET /api/trigger-definitions — trigger types available for the caller's
   * *connected* services. Optional `service` filters to one service slug.
   */
  async listTriggerDefinitions(accessToken: string, service?: string) {
    const path = service
      ? `/api/trigger-definitions?${new URLSearchParams({ service })}`
      : "/api/trigger-definitions";

    return this.request<ListTriggerDefinitionsResponse>(path, {
      method: "GET",
      accessToken,
    });
  }

  /**
   * POST /api/triggers — subscribe to a trigger for a connected account.
   * The response's `signing_secret` is only ever returned this once.
   */
  async subscribeTrigger(accessToken: string, params: SubscribeTriggerParams) {
    return this.request<SubscribeTriggerResponse>("/api/triggers", {
      method: "POST",
      accessToken,
      body: {
        service: params.service,
        trigger: params.trigger,
        config: params.config,
        callback_url: params.callbackUrl,
      },
    });
  }

  /** GET /api/triggers — list the caller's trigger instances. */
  async listTriggerInstances(accessToken: string) {
    return this.request<ListTriggerInstancesResponse>("/api/triggers", {
      method: "GET",
      accessToken,
    });
  }

  /** GET /api/triggers/{id} */
  async getTriggerInstance(accessToken: string, id: string) {
    return this.request<GetTriggerInstanceResponse>(`/api/triggers/${id}`, {
      method: "GET",
      accessToken,
    });
  }

  /**
   * PATCH /api/triggers/{id} — pause/resume via `status`, or update
   * `callbackUrl`/`config`. At least one field must be supplied.
   */
  async updateTriggerInstance(accessToken: string, id: string, patch: UpdateTriggerInstanceParams) {
    return this.request<UpdateTriggerInstanceResponse>(`/api/triggers/${id}`, {
      method: "PATCH",
      accessToken,
      body: {
        status: patch.status,
        callback_url: patch.callbackUrl,
        config: patch.config,
      },
    });
  }

  /**
   * DELETE /api/triggers/{id} — unsubscribes and, if it was the last
   * instance sharing a provider-side webhook registration, deregisters it.
   */
  async unsubscribeTrigger(accessToken: string, id: string) {
    return this.request<UnsubscribeTriggerResponse>(`/api/triggers/${id}`, {
      method: "DELETE",
      accessToken,
    });
  }

  /**
   * GET /api/triggers/{id}/deliveries — paginated delivery log for one
   * trigger instance, each with its latest HTTP attempt joined in.
   */
  async listDeliveries(
    accessToken: string,
    triggerInstanceId: string,
    opts: ListDeliveriesOptions = {},
  ) {
    const params = new URLSearchParams();
    if (opts.status !== undefined) {
      params.set("status", opts.status);
    }
    if (opts.limit !== undefined) {
      params.set("limit", String(opts.limit));
    }
    if (opts.cursor !== undefined) {
      params.set("cursor", opts.cursor);
    }
    const query = params.toString();
    const path = `/api/triggers/${triggerInstanceId}/deliveries${query ? `?${query}` : ""}`;

    return this.request<ListDeliveriesResponse>(path, {
      method: "GET",
      accessToken,
    });
  }

  private async request<T>(
    path: string,
    options: {
      method: string;
      body?: unknown;
      accessToken?: string;
    },
  ): Promise<T> {
    const headers: Record<string, string> = {
      Accept: "application/json",
    };

    if (options.body !== undefined) {
      headers["Content-Type"] = "application/json";
    }

    if (options.accessToken) {
      headers.Authorization = `Bearer ${options.accessToken}`;
    }

    const response = await this.fetchImpl(`${this.baseUrl}${path}`, {
      method: options.method,
      headers,
      body: options.body === undefined ? undefined : JSON.stringify(options.body),
    });

    const payload = await response.json().catch(() => null);
    if (!response.ok || payload?.success === false) {
      throw new AppConnectError(
        payload?.error?.message || response.statusText,
        response.status,
        payload?.error?.code,
      );
    }

    return payload?.data as T;
  }
}
