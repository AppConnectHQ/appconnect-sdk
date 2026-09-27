# @appconnecthq/sdk

The main entry point: `AppConnectClient`, its request and response types,
webhook signature verification, and the dependency-free OpenAI and
Anthropic tool adapters.

## Classes

### AppConnectClient

#### Constructors

##### Constructor

```ts
new AppConnectClient(options): AppConnectClient;
```

###### Parameters

| Parameter | Type |
| ------ | ------ |
| `options` | [`AppConnectClientOptions`](#appconnectclientoptions) |

###### Returns

[`AppConnectClient`](#appconnectclient)

#### Methods

##### createLinkToken()

```ts
createLinkToken(params): Promise<CreateLinkTokenResponse>;
```

###### Parameters

| Parameter | Type |
| ------ | ------ |
| `params` | [`CreateLinkTokenParams`](#createlinktokenparams) |

###### Returns

`Promise`\<[`CreateLinkTokenResponse`](#createlinktokenresponse)\>

##### exchangeAuthorizationCode()

```ts
exchangeAuthorizationCode(code, redirectUri): Promise<TokenResponse>;
```

###### Parameters

| Parameter | Type |
| ------ | ------ |
| `code` | `string` |
| `redirectUri` | `string` |

###### Returns

`Promise`\<[`TokenResponse`](#tokenresponse)\>

##### exchangeLinkToken()

```ts
exchangeLinkToken(linkToken): Promise<ExchangeLinkTokenResponse>;
```

###### Parameters

| Parameter | Type |
| ------ | ------ |
| `linkToken` | `string` |

###### Returns

`Promise`\<[`ExchangeLinkTokenResponse`](#exchangelinktokenresponse)\>

##### executeTool()

```ts
executeTool<T>(
   accessToken, 
   tool, 
   params?
): Promise<ToolExecutionResponse<T>>;
```

###### Type Parameters

| Type Parameter | Default type |
| ------ | ------ |
| `T` | `unknown` |

###### Parameters

| Parameter | Type |
| ------ | ------ |
| `accessToken` | `string` |
| `tool` | `string` |
| `params` | `Record`\<`string`, `unknown`\> |

###### Returns

`Promise`\<[`ToolExecutionResponse`](#toolexecutionresponse)\<`T`\>\>

##### getTriggerInstance()

```ts
getTriggerInstance(accessToken, id): Promise<GetTriggerInstanceResponse>;
```

GET /api/triggers/\{id\}

###### Parameters

| Parameter | Type |
| ------ | ------ |
| `accessToken` | `string` |
| `id` | `string` |

###### Returns

`Promise`\<[`GetTriggerInstanceResponse`](#gettriggerinstanceresponse)\>

##### listDeliveries()

```ts
listDeliveries(
   accessToken, 
   triggerInstanceId, 
   opts?
): Promise<ListDeliveriesResponse>;
```

GET /api/triggers/\{id\}/deliveries — paginated delivery log for one
trigger instance, each with its latest HTTP attempt joined in.

###### Parameters

| Parameter | Type |
| ------ | ------ |
| `accessToken` | `string` |
| `triggerInstanceId` | `string` |
| `opts` | [`ListDeliveriesOptions`](#listdeliveriesoptions) |

###### Returns

`Promise`\<[`ListDeliveriesResponse`](#listdeliveriesresponse)\>

##### listTools()

```ts
listTools(accessToken): Promise<ListToolsResponse>;
```

###### Parameters

| Parameter | Type |
| ------ | ------ |
| `accessToken` | `string` |

###### Returns

`Promise`\<[`ListToolsResponse`](#listtoolsresponse)\>

##### listTriggerDefinitions()

```ts
listTriggerDefinitions(accessToken, service?): Promise<ListTriggerDefinitionsResponse>;
```

GET /api/trigger-definitions — trigger types available for the caller's
*connected* services. Optional `service` filters to one service slug.

###### Parameters

| Parameter | Type |
| ------ | ------ |
| `accessToken` | `string` |
| `service?` | `string` |

###### Returns

`Promise`\<[`ListTriggerDefinitionsResponse`](#listtriggerdefinitionsresponse)\>

##### listTriggerInstances()

```ts
listTriggerInstances(accessToken): Promise<ListTriggerInstancesResponse>;
```

GET /api/triggers — list the caller's trigger instances.

###### Parameters

| Parameter | Type |
| ------ | ------ |
| `accessToken` | `string` |

###### Returns

`Promise`\<[`ListTriggerInstancesResponse`](#listtriggerinstancesresponse)\>

##### proxy()

```ts
proxy<T>(
   accessToken, 
   service, 
   path, 
   init?
): Promise<T>;
```

###### Type Parameters

| Type Parameter | Default type |
| ------ | ------ |
| `T` | `unknown` |

###### Parameters

| Parameter | Type |
| ------ | ------ |
| `accessToken` | `string` |
| `service` | `string` |
| `path` | `string` |
| `init` | `Omit`\<`RequestInit`, `"headers"` \| `"body"`\> & `object` |

###### Returns

`Promise`\<`T`\>

##### refreshToken()

```ts
refreshToken(refreshToken): Promise<TokenResponse>;
```

###### Parameters

| Parameter | Type |
| ------ | ------ |
| `refreshToken` | `string` |

###### Returns

`Promise`\<[`TokenResponse`](#tokenresponse)\>

##### searchTools()

```ts
searchTools(
   accessToken, 
   query, 
   limit?
): Promise<SearchToolsResponse>;
```

###### Parameters

| Parameter | Type |
| ------ | ------ |
| `accessToken` | `string` |
| `query` | `string` |
| `limit?` | `number` |

###### Returns

`Promise`\<[`SearchToolsResponse`](#searchtoolsresponse)\>

##### subscribeTrigger()

```ts
subscribeTrigger(accessToken, params): Promise<SubscribeTriggerResponse>;
```

POST /api/triggers — subscribe to a trigger for a connected account.
The response's `signing_secret` is only ever returned this once.

###### Parameters

| Parameter | Type |
| ------ | ------ |
| `accessToken` | `string` |
| `params` | [`SubscribeTriggerParams`](#subscribetriggerparams) |

###### Returns

`Promise`\<[`SubscribeTriggerResponse`](#subscribetriggerresponse)\>

##### unsubscribeTrigger()

```ts
unsubscribeTrigger(accessToken, id): Promise<UnsubscribeTriggerResponse>;
```

DELETE /api/triggers/\{id\} — unsubscribes and, if it was the last
instance sharing a provider-side webhook registration, deregisters it.

###### Parameters

| Parameter | Type |
| ------ | ------ |
| `accessToken` | `string` |
| `id` | `string` |

###### Returns

`Promise`\<[`UnsubscribeTriggerResponse`](#unsubscribetriggerresponse)\>

##### updateTriggerInstance()

```ts
updateTriggerInstance(
   accessToken, 
   id, 
   patch
): Promise<UpdateTriggerInstanceResponse>;
```

PATCH /api/triggers/\{id\} — pause/resume via `status`, or update
`callbackUrl`/`config`. At least one field must be supplied.

###### Parameters

| Parameter | Type |
| ------ | ------ |
| `accessToken` | `string` |
| `id` | `string` |
| `patch` | [`UpdateTriggerInstanceParams`](#updatetriggerinstanceparams) |

###### Returns

`Promise`\<[`UpdateTriggerInstanceResponse`](#updatetriggerinstanceresponse)\>

***

### AppConnectError

#### Extends

- `Error`

#### Constructors

##### Constructor

```ts
new AppConnectError(
   message, 
   status, 
   code?
): AppConnectError;
```

###### Parameters

| Parameter | Type |
| ------ | ------ |
| `message` | `string` |
| `status` | `number` |
| `code?` | `string` |

###### Returns

[`AppConnectError`](#appconnecterror)

###### Overrides

```ts
Error.constructor
```

#### Properties

| Property | Modifier | Type | Description | Inherited from |
| ------ | ------ | ------ | ------ | ------ |
| <a id="property-cause"></a> `cause?` | `public` | `unknown` | - | `Error.cause` |
| <a id="property-code"></a> `code?` | `readonly` | `string` | - | - |
| <a id="property-message"></a> `message` | `public` | `string` | - | `Error.message` |
| <a id="property-name"></a> `name` | `public` | `string` | - | `Error.name` |
| <a id="property-stack"></a> `stack?` | `public` | `string` | - | `Error.stack` |
| <a id="property-status"></a> `status` | `readonly` | `number` | - | - |
| <a id="property-stacktracelimit"></a> `stackTraceLimit` | `static` | `number` | The `Error.stackTraceLimit` property specifies the number of stack frames collected by a stack trace (whether generated by `new Error().stack` or `Error.captureStackTrace(obj)`). The default value is `10` but may be set to any valid JavaScript number. Changes will affect any stack trace captured _after_ the value has been changed. If set to a non-number value, or set to a negative number, stack traces will not capture any frames. | `Error.stackTraceLimit` |

#### Methods

##### captureStackTrace()

```ts
static captureStackTrace(targetObject, constructorOpt?): void;
```

Creates a `.stack` property on `targetObject`, which when accessed returns
a string representing the location in the code at which
`Error.captureStackTrace()` was called.

```js
const myObject = {};
Error.captureStackTrace(myObject);
myObject.stack;  // Similar to `new Error().stack`
```

The first line of the trace will be prefixed with
`${myObject.name}: ${myObject.message}`.

The optional `constructorOpt` argument accepts a function. If given, all frames
above `constructorOpt`, including `constructorOpt`, will be omitted from the
generated stack trace.

The `constructorOpt` argument is useful for hiding implementation
details of error generation from the user. For instance:

```js
function a() {
  b();
}

function b() {
  c();
}

function c() {
  // Create an error without stack trace to avoid calculating the stack trace twice.
  const { stackTraceLimit } = Error;
  Error.stackTraceLimit = 0;
  const error = new Error();
  Error.stackTraceLimit = stackTraceLimit;

  // Capture the stack trace above function b
  Error.captureStackTrace(error, b); // Neither function c, nor b is included in the stack trace
  throw error;
}

a();
```

###### Parameters

| Parameter | Type |
| ------ | ------ |
| `targetObject` | `object` |
| `constructorOpt?` | `Function` |

###### Returns

`void`

###### Inherited from

```ts
Error.captureStackTrace
```

##### isError()

```ts
static isError(error): error is Error;
```

Indicates whether the argument provided is a built-in Error instance or not.

###### Parameters

| Parameter | Type |
| ------ | ------ |
| `error` | `unknown` |

###### Returns

`error is Error`

###### Inherited from

```ts
Error.isError
```

##### prepareStackTrace()

```ts
static prepareStackTrace(err, stackTraces): any;
```

###### Parameters

| Parameter | Type |
| ------ | ------ |
| `err` | `Error` |
| `stackTraces` | `CallSite`[] |

###### Returns

`any`

###### See

https://v8.dev/docs/stack-trace-api#customizing-stack-traces

###### Inherited from

```ts
Error.prepareStackTrace
```

## Interfaces

### AnthropicTool

A tool in Anthropic Messages API tool-use shape.

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-description"></a> `description` | `string` |
| <a id="property-input_schema"></a> `input_schema` | `object` |
| `input_schema.properties` | `Record`\<`string`, `unknown`\> |
| `input_schema.required?` | `string`[] |
| `input_schema.type` | `"object"` |
| <a id="property-name-1"></a> `name` | `string` |

***

### AnthropicToolResultBlock

The `tool_result` content block Anthropic expects in the following user turn.

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-content"></a> `content` | `string` |
| <a id="property-tool_use_id"></a> `tool_use_id` | `string` |
| <a id="property-type"></a> `type` | `"tool_result"` |

***

### AnthropicToolUseBlock

A `tool_use` content block from an Anthropic assistant message.

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-id"></a> `id` | `string` |
| <a id="property-input"></a> `input` | `Record`\<`string`, `unknown`\> |
| <a id="property-name-2"></a> `name` | `string` |
| <a id="property-type-1"></a> `type` | `"tool_use"` |

***

### AppConnectClientOptions

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-baseurl"></a> `baseUrl?` | `string` |
| <a id="property-clientid"></a> `clientId` | `string` |
| <a id="property-clientsecret"></a> `clientSecret` | `string` |
| <a id="property-fetch"></a> `fetch?` | \{ (`input`, `init?`): `Promise`\<`Response`\>; (`input`, `init?`): `Promise`\<`Response`\>; \} |

***

### AppConnectDelivery

A queued/delivered event row, as returned by
GET /api/triggers/\{id\}/deliveries. Mirrors the server's `PublicDelivery`
response shape.

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-attempts"></a> `attempts` | `number` |
| <a id="property-createdat"></a> `createdAt` | `string` |
| <a id="property-eventid"></a> `eventId` | `string` |
| <a id="property-eventtype"></a> `eventType` | `string` |
| <a id="property-id-1"></a> `id` | `string` |
| <a id="property-lastattemptat"></a> `lastAttemptAt` | `string` \| `null` |
| <a id="property-lasterror"></a> `lastError` | `string` \| `null` |
| <a id="property-laststatuscode"></a> `lastStatusCode` | `number` \| `null` |
| <a id="property-latestattempt"></a> `latestAttempt` | [`AppConnectDeliveryAttempt`](#appconnectdeliveryattempt) \| `null` |
| <a id="property-maxattempts"></a> `maxAttempts` | `number` |
| <a id="property-nextattemptat"></a> `nextAttemptAt` | `string` |
| <a id="property-status-1"></a> `status` | `string` |
| <a id="property-updatedat"></a> `updatedAt` | `string` |

***

### AppConnectDeliveryAttempt

One HTTP attempt at delivering an event to a trigger instance's `callbackUrl`.

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-attemptnumber"></a> `attemptNumber` | `number` |
| <a id="property-createdat-1"></a> `createdAt` | `string` |
| <a id="property-errormessage"></a> `errorMessage` | `string` \| `null` |
| <a id="property-latencyms"></a> `latencyMs` | `number` \| `null` |
| <a id="property-statuscode"></a> `statusCode` | `number` \| `null` |

***

### AppConnectTool

A tool exposed by a connected service, as returned by GET /api/tools and
GET /api/tools/search. Mirrors the server's `listUserTools`
response shape.

#### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| <a id="property-description-1"></a> `description` | `string` \| `null` | - |
| <a id="property-displayname"></a> `displayName` | `string` | - |
| <a id="property-id-2"></a> `id` | `string` | Unified tool id, e.g. "google_calendar_list_events" — what executeTool expects. |
| <a id="property-inputschema"></a> `inputSchema` | \| \{ `properties?`: `Record`\<`string`, `unknown`\>; `required?`: `string`[]; `type`: `string`; \} \| `null` | - |
| <a id="property-method"></a> `method` | `"GET"` \| `"POST"` \| `"PUT"` \| `"PATCH"` \| `"DELETE"` | - |
| <a id="property-name-3"></a> `name` | `string` | Tool name within the service, e.g. "list_events". |
| <a id="property-service"></a> `service` | `string` | Service slug, e.g. "google-calendar". |
| <a id="property-servicename"></a> `serviceName` | `string` | - |

***

### AppConnectTriggerDefinition

A trigger type available for a connected service, as returned by
GET /api/trigger-definitions. Mirrors the server's `listUserTriggerDefinitions`
response shape.

#### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| <a id="property-configschema"></a> `configSchema` | `unknown` | JSON Schema describing what `subscribeTrigger`'s `config` must supply. |
| <a id="property-description-2"></a> `description` | `string` \| `null` | - |
| <a id="property-displayname-1"></a> `displayName` | `string` | - |
| <a id="property-id-3"></a> `id` | `string` | - |
| <a id="property-mode"></a> `mode` | `"webhook"` \| `"polling"` | - |
| <a id="property-payloadschema"></a> `payloadSchema` | `unknown` | JSON Schema documenting the normalized payload shape delivered to `callbackUrl`. |
| <a id="property-service-1"></a> `service` | `string` | - |
| <a id="property-servicename-1"></a> `serviceName` | `string` | - |
| <a id="property-slug"></a> `slug` | `string` | Trigger type slug within the service, e.g. "new_commit". |

***

### AppConnectTriggerInstance

A subscription to a trigger for a connected account, as returned by
`api/triggers*`. Mirrors the server's `PublicTriggerInstance`
response shape.

#### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| <a id="property-callbackurl"></a> `callbackUrl` | `string` | - |
| <a id="property-config"></a> `config` | `Record`\<`string`, `unknown`\> | - |
| <a id="property-createdat-2"></a> `createdAt` | `string` | - |
| <a id="property-errormessage-1"></a> `errorMessage` | `string` \| `null` | - |
| <a id="property-id-4"></a> `id` | `string` | - |
| <a id="property-lasteventat"></a> `lastEventAt` | `string` \| `null` | - |
| <a id="property-lastpolledat"></a> `lastPolledAt` | `string` \| `null` | - |
| <a id="property-service-2"></a> `service` | `string` | - |
| <a id="property-status-2"></a> `status` | `string` | - |
| <a id="property-trigger"></a> `trigger` | `string` | Trigger definition slug this instance subscribes to, e.g. "new_commit". |
| <a id="property-updatedat-1"></a> `updatedAt` | `string` | - |

***

### ConnectedLinkExchangeResponse

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-access_token"></a> `access_token` | `string` |
| <a id="property-connected_services"></a> `connected_services` | `string`[] |
| <a id="property-expires_at"></a> `expires_at` | `string` |
| <a id="property-refresh_token"></a> `refresh_token` | `string` |
| <a id="property-state"></a> `state?` | `string` \| `null` |
| <a id="property-status-3"></a> `status` | `"connected"` |
| <a id="property-token_type"></a> `token_type` | `"Bearer"` |
| <a id="property-user_id"></a> `user_id` | `string` |

***

### CreateLinkTokenParams

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-allowedservices"></a> `allowedServices?` | `string`[] |
| <a id="property-expiresin"></a> `expiresIn?` | `number` |
| <a id="property-redirecturi"></a> `redirectUri` | `string` |
| <a id="property-state-1"></a> `state?` | `string` |
| <a id="property-userid"></a> `userId` | `string` |

***

### CreateLinkTokenResponse

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-expires_at-1"></a> `expires_at` | `string` |
| <a id="property-link_token"></a> `link_token` | `string` |
| <a id="property-link_url"></a> `link_url` | `string` |

***

### GetTriggerInstanceResponse

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-trigger-1"></a> `trigger` | [`AppConnectTriggerInstance`](#appconnecttriggerinstance) |

***

### JsonSchemaObject

The top-level shape AppConnectTool.inputSchema carries over the wire.

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-properties"></a> `properties?` | `Record`\<`string`, `unknown`\> |
| <a id="property-required"></a> `required?` | `string`[] |
| <a id="property-type-2"></a> `type` | `string` |

***

### JsonSchemaProperty

A flat JSON Schema property, matching the shapes AppConnect actually
emits in tool input schemas. This is not a
general JSON Schema implementation -- only the subset AppConnect uses:
string/number/integer/boolean/array/object, `enum`, `description`, and a
recursive `items`/`properties` for arrays and nested objects.

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-default"></a> `default?` | `unknown` |
| <a id="property-description-3"></a> `description?` | `string` |
| <a id="property-enum"></a> `enum?` | `string`[] |
| <a id="property-format"></a> `format?` | `string` |
| <a id="property-items"></a> `items?` | [`JsonSchemaProperty`](#jsonschemaproperty) |
| <a id="property-properties-1"></a> `properties?` | `Record`\<`string`, `unknown`\> |
| <a id="property-required-1"></a> `required?` | `string`[] |
| <a id="property-type-3"></a> `type?` | `string` |

***

### ListDeliveriesOptions

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-cursor"></a> `cursor?` | `string` |
| <a id="property-limit"></a> `limit?` | `number` |
| <a id="property-status-4"></a> `status?` | `string` |

***

### ListDeliveriesResponse

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-deliveries"></a> `deliveries` | [`AppConnectDelivery`](#appconnectdelivery)[] |
| <a id="property-nextcursor"></a> `nextCursor` | `string` \| `null` |

***

### ListToolsResponse

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-tools"></a> `tools` | [`AppConnectTool`](#appconnecttool)[] |

***

### ListTriggerDefinitionsResponse

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-trigger_definitions"></a> `trigger_definitions` | [`AppConnectTriggerDefinition`](#appconnecttriggerdefinition)[] |

***

### ListTriggerInstancesResponse

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-triggers"></a> `triggers` | [`AppConnectTriggerInstance`](#appconnecttriggerinstance)[] |

***

### OpenAIFunctionTool

A tool in OpenAI chat-completions function-calling shape.

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-function"></a> `function` | `object` |
| `function.description` | `string` |
| `function.name` | `string` |
| `function.parameters` | `object` |
| `function.parameters.properties` | `Record`\<`string`, `unknown`\> |
| `function.parameters.required?` | `string`[] |
| `function.parameters.type` | `"object"` |
| <a id="property-type-4"></a> `type` | `"function"` |

***

### OpenAIToolCall

An OpenAI chat-completions tool call, as found on an assistant message's `tool_calls`.

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-function-1"></a> `function` | `object` |
| `function.arguments` | `string` |
| `function.name` | `string` |
| <a id="property-id-5"></a> `id` | `string` |

***

### OpenAIToolResultMessage

The `{role: "tool", ...}` message OpenAI expects appended after a tool call runs.

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-content-1"></a> `content` | `string` |
| <a id="property-role"></a> `role` | `"tool"` |
| <a id="property-tool_call_id"></a> `tool_call_id` | `string` |

***

### PendingLinkExchangeResponse

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-message-1"></a> `message` | `string` |
| <a id="property-state-2"></a> `state?` | `string` \| `null` |
| <a id="property-status-5"></a> `status` | `"pending"` |
| <a id="property-user_id-1"></a> `user_id` | `string` |

***

### SearchToolsResponse

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-query"></a> `query` | `string` |
| <a id="property-tools-1"></a> `tools` | [`AppConnectTool`](#appconnecttool)[] |

***

### SubscribeTriggerParams

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-callbackurl-1"></a> `callbackUrl` | `string` |
| <a id="property-config-1"></a> `config` | `Record`\<`string`, `unknown`\> |
| <a id="property-service-3"></a> `service` | `string` |
| <a id="property-trigger-2"></a> `trigger` | `string` |

***

### SubscribeTriggerResponse

#### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| <a id="property-signing_secret"></a> `signing_secret` | `string` | Returned exactly once — store it yourself to verify `X-AppConnect-Signature` on inbound deliveries via `verifyWebhookSignature()`. Subsequent GETs never return it again. |
| <a id="property-trigger-3"></a> `trigger` | [`AppConnectTriggerInstance`](#appconnecttriggerinstance) | - |

***

### TokenResponse

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-access_token-1"></a> `access_token` | `string` |
| <a id="property-connected_services-1"></a> `connected_services` | `string`[] |
| <a id="property-expires_in"></a> `expires_in` | `number` |
| <a id="property-refresh_token-1"></a> `refresh_token` | `string` |
| <a id="property-token_type-1"></a> `token_type` | `"Bearer"` |

***

### ToolAdapterOptions

Shared contract for every framework adapter (OpenAI, Anthropic, ...).

AppConnect's client is multi-tenant per-request — every call needs an
`accessToken` — so unlike single-tenant SDKs, adapters thread the token
explicitly instead of storing it on the client.

#### Properties

| Property | Type | Description |
| ------ | ------ | ------ |
| <a id="property-accesstoken"></a> `accessToken` | `string` | Bearer token identifying the connected user. |
| <a id="property-client"></a> `client` | [`AppConnectClient`](#appconnectclient) | The AppConnectClient used to list/execute tools. |
| <a id="property-tools-2"></a> `tools?` | [`AppConnectTool`](#appconnecttool)[] | Pass pre-fetched tools to skip a listTools() round trip. |

***

### ToolExecutionResponse

#### Type Parameters

| Type Parameter | Default type |
| ------ | ------ |
| `T` | `unknown` |

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-data"></a> `data` | `T` |
| <a id="property-tool"></a> `tool` | `string` |

***

### UnsubscribeTriggerResponse

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-revoked"></a> `revoked` | `true` |

***

### UpdateTriggerInstanceParams

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-callbackurl-2"></a> `callbackUrl?` | `string` |
| <a id="property-config-2"></a> `config?` | `Record`\<`string`, `unknown`\> |
| <a id="property-status-6"></a> `status?` | `"active"` \| `"paused"` |

***

### UpdateTriggerInstanceResponse

#### Properties

| Property | Type |
| ------ | ------ |
| <a id="property-trigger-4"></a> `trigger` | [`AppConnectTriggerInstance`](#appconnecttriggerinstance) |

## Type Aliases

### ExchangeLinkTokenResponse

```ts
type ExchangeLinkTokenResponse = 
  | PendingLinkExchangeResponse
  | ConnectedLinkExchangeResponse;
```

## Variables

### DEFAULT\_BASE\_URL

```ts
const DEFAULT_BASE_URL: "https://www.appconnecthq.com" = "https://www.appconnecthq.com";
```

## Functions

### executeAnthropicToolUse()

```ts
function executeAnthropicToolUse(options, toolUse): Promise<AnthropicToolResultBlock>;
```

Executes a single Anthropic `tool_use` block via `executeTool` and
returns the `tool_result` content block to append to the next user turn.

#### Parameters

| Parameter | Type |
| ------ | ------ |
| `options` | [`ToolAdapterOptions`](#tooladapteroptions) |
| `toolUse` | [`AnthropicToolUseBlock`](#anthropictooluseblock) |

#### Returns

`Promise`\<[`AnthropicToolResultBlock`](#anthropictoolresultblock)\>

***

### executeOpenAIToolCall()

```ts
function executeOpenAIToolCall(options, toolCall): Promise<OpenAIToolResultMessage>;
```

Executes a single OpenAI tool call via `executeTool` and returns the
`{role: "tool", ...}` message to append to the conversation.

#### Parameters

| Parameter | Type |
| ------ | ------ |
| `options` | [`ToolAdapterOptions`](#tooladapteroptions) |
| `toolCall` | [`OpenAIToolCall`](#openaitoolcall) |

#### Returns

`Promise`\<[`OpenAIToolResultMessage`](#openaitoolresultmessage)\>

***

### jsonSchemaObjectToZod()

```ts
function jsonSchemaObjectToZod(schema): ZodObject<Record<string, ZodTypeAny<unknown, unknown, $ZodTypeInternals<unknown, unknown>>>>;
```

Converts an AppConnect-shaped JSON Schema object (top-level or nested)
into a Zod object schema, marking properties absent from `required` as
optional. This is the shape LangChain's `DynamicStructuredTool` expects
for its `schema` field.

#### Parameters

| Parameter | Type |
| ------ | ------ |
| `schema` | [`JsonSchemaObject`](#jsonschemaobject) \| `null` \| `undefined` |

#### Returns

`ZodObject`\<`Record`\<`string`, `ZodTypeAny`\<`unknown`, `unknown`, `$ZodTypeInternals`\<`unknown`, `unknown`\>\>\>\>

***

### jsonSchemaPropertyToZod()

```ts
function jsonSchemaPropertyToZod(prop): ZodTypeAny;
```

Converts a single JSON Schema property into a Zod schema. Falls back to
`z.unknown()` for shapes outside AppConnect's flat property model
(missing/unrecognized `type`, etc.) rather than throwing -- a tool schema
should still construct successfully even if one property is unusual.

#### Parameters

| Parameter | Type |
| ------ | ------ |
| `prop` | `unknown` |

#### Returns

`ZodTypeAny`

***

### toAnthropicTools()

```ts
function toAnthropicTools(options): Promise<AnthropicTool[]>;
```

Maps AppConnect tools to Anthropic Messages API tool-use tools.

#### Parameters

| Parameter | Type |
| ------ | ------ |
| `options` | [`ToolAdapterOptions`](#tooladapteroptions) |

#### Returns

`Promise`\<[`AnthropicTool`](#anthropictool)[]\>

***

### toOpenAITools()

```ts
function toOpenAITools(options): Promise<OpenAIFunctionTool[]>;
```

Maps AppConnect tools to OpenAI chat-completions function-calling tools.

#### Parameters

| Parameter | Type |
| ------ | ------ |
| `options` | [`ToolAdapterOptions`](#tooladapteroptions) |

#### Returns

`Promise`\<[`OpenAIFunctionTool`](#openaifunctiontool)[]\>

***

### verifyWebhookSignature()

```ts
function verifyWebhookSignature(
   rawBody, 
   header, 
   signingSecret, 
   toleranceSeconds?
): boolean;
```

Partner-side verification for AppConnect's outbound trigger deliveries.

A partner's own webhook receiver calls this against the raw request body
and the `X-AppConnect-Signature: t=<unix_ts>,v1=<hex hmac>` header, using
the `signing_secret` returned once from `subscribeTrigger()`. It mirrors
AppConnect's server-side signer byte-for-byte: both HMAC-SHA256 the string
`${t}.${rawBody}` with the shared secret and compare hex digests.

Exported standalone (not an `AppConnectClient` method) since it runs
inside the partner's own webhook handler, not against AppConnect's API.

#### Parameters

| Parameter | Type | Default value |
| ------ | ------ | ------ |
| `rawBody` | `string` | `undefined` |
| `header` | `string` | `undefined` |
| `signingSecret` | `string` | `undefined` |
| `toleranceSeconds` | `number` | `300` |

#### Returns

`boolean`
