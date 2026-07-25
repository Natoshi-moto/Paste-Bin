# NEXUS Room, LOOM, and Connectivity Specification

## A human/agent/P2P workspace with a private cryptographic spine

**Document status:** engineering specification and contributor guide  
**Observed source date:** 2026-07-25  
**Repository branch observed:** `sandbox/experiment/natoshi-assistant-matrix-terminal`  
**Publication status:** local working document; not a release, commit, or approval  
**Authority:** `status_authority: NONE`

This document is the build map for the NEXUS “spaceship”: a compact,
terminal-first human/agent workspace whose useful state can be inspected,
replayed, carried over different media, and proposed to Git without making the
network, a model, or a summary authoritative.

It is deliberately stricter than the product vision. Anything described here is
labelled with one of four evidence states:

| Label | Meaning |
|---|---|
| **IMPLEMENTED / TESTED** | Code exists and a named automated test exercised the property during this audit or in the recorded implementation checkpoint. |
| **IMPLEMENTED / TEST GAP** | Code exists, but the current audit did not establish a completely green test gate for it. |
| **SPECIFIED / INERT** | The interface, policy, or stub exists, but it has no live external effect. |
| **REJECTED** | Deliberately outside the product boundary. Contributors must not smuggle it back under a different name. |

“Implemented” never means deployed, independently audited, secure against every
host compromise, or suitable for financial custody.

---

## 1. Product sentence

NEXUS is a local-first cockpit where a human and multiple bounded agents can
talk, retrieve evidence, divide work, exchange encrypted Drops, and build a
replayable project record while every transition preserves its source,
authority, privacy, and execution boundary.

The flagship optional flow is:

```text
CAPTURE OFF by default
  -> exact local source record
  -> deterministic preflight and secret scrub
  -> explicit approval of the exact scrubbed hash and provider families
  -> DeepSeek as the first external processor
  -> a higher-ranked, nonlocal, distinct-family second reviewer
  -> deterministic candidate validation
  -> explicit inert Git commit proposal
  -> separate human-controlled Git execution, if ever approved
```

GitHub may become an opt-in, reviewable history of **scrubbed derivatives** and
their provenance. It is not a destination for raw private sessions, API keys,
private room ciphertext by default, or automatic publication.

---

## 2. Canonical boundaries

These boundaries outrank convenience, model consensus, mission names, and UI
copy.

### 2.1 What NEXUS may prove

Depending on the object and validation path, NEXUS may prove narrowly scoped
facts such as:

- these exact bytes hash to this digest;
- this Ed25519 key signed this canonical envelope;
- this event extended this locally accepted room head;
- two replicas using the same policy, key epoch, and ordered events replayed to
  the same state root;
- this recipient key could authenticate and decrypt this Drop;
- this accepted local custody history consumed one output and created one
  successor;
- this model proposal came after the approved scrubbed hash and was recorded
  under the declared provider/model/family metadata;
- this proposed Git artifact is bound to the reviewed candidate hash.

### 2.2 What NEXUS does not prove

The following are **REJECTED** as product claims:

- plaintext non-copyability after an authorised recipient decrypts it;
- universal truth, universal availability, or universal finality;
- permissionless consensus;
- legal or financial settlement;
- that multiple agreeing models are independent evidence;
- that a route, index, summary, model output, Git commit, or observer receipt is
  authoritative merely because it exists;
- anonymous “forced governance,” coercive participation, or governance with no
  human exit;
- unrestricted `sudo`, root, passwordless elevation, or raw model text as a
  shell command;
- automatic commit, push, merge, or publication;
- hidden browser/session scraping, login-cookie reuse, or invisible microphone
  capture;
- encrypted amateur-radio transmission or live ham-radio transmit/PTT control;
- modifying the Tails trust base;
- importing RoomFinal as legal settlement or WinMX as a live file-sharing
  network.

### 2.3 RoomFinal drift anchor

The room layer creates:

> Policy-scoped evidence over trusted ordered room state; not permissionless
> consensus, legal settlement, universal truth, or universal finality.

An observer signature proves only that the observer signed a reference to an
envelope. A checkpoint proves only a policy-bound claim about an ordered local
state under a named reducer and allowed signer set.

### 2.4 Human sovereignty

Routine assignment may be deterministic and autonomous. Membership, policy,
provider disclosure, privacy approval, commit execution, publication, recovery,
and emergency stop remain human-governed.

“No human micromanagement” means a stable reducer can perform routine scheduling.
It does not mean removing consent, recourse, ownership, or a kill switch.

---

## 3. Current implementation map

| Surface | Current state | Evidence and limits |
|---|---|---|
| Compact Tk cockpit | **IMPLEMENTED / TESTED elsewhere** | Terminal-first responsive app, model bay, evidence deck, top commentary, API vault, commands, Room/LOOM bay. Live deployment is a separate evidence question. |
| Twin PILOT/WITNESS route | **IMPLEMENTED / TESTED elsewhere** | Distinct direct PILOT candidates plus a required local Ollama WITNESS; WITNESS can withhold an unchecked answer when required review fails. |
| Evidence packets | **IMPLEMENTED / TESTED elsewhere** | Atomic Linux file store, explicit PILOT/WITNESS/BOTH attachment, `status_authority=NONE`. Storage is permission-bounded, not encrypted by this module. |
| Encrypted room | **IMPLEMENTED / TESTED** | Real Ed25519 and ChaCha20-Poly1305, canonical replay, scoped receipts/checkpoints. All eleven room tests passed in the final focused audit. |
| Greywire Drop | **IMPLEMENTED / TESTED** | X25519, HKDF-SHA256, ChaCha20-Poly1305, Ed25519 manifest, deterministic in-memory single-live-output custody. Eight tests passed during this audit. |
| Connector registry and fixture quarantine | **IMPLEMENTED / TESTED** | 25 inert connectors, zero live endpoints, deterministic ingress state machine. Fifteen tests passed during this audit. |
| LOOM archive + Forge railway | **IMPLEMENTED / TESTED LOCALLY; LIVE CLOUD UNPROVEN** | Capture defaults OFF. A Secret-Service-backed ChaCha20-Poly1305 archive stores canonical exact-byte events in a locked, fsynced, `0600` hash chain. Forge enforces sealed-reference, scrub/hash approval, DeepSeek-first, distinct higher-rank review, deterministic validation, and inert commit proposal. The runtime bridge can call configured external adapters, but no credentialed cloud run is claimed here. No Git execution or publication is implemented. |
| Browser organ | **IMPLEMENTED LOCAL SCAFFOLD** | User-triggered selected/page excerpts, reviewed voice draft, explicit ChatGPT copy handoff, native messaging. Not installed, signed, or store-published. |
| Live Nostr/IRC/Discord/Slack/etc. | **SPECIFIED / INERT** | Typed registry metadata and fixture processing only. |
| Privileged Nexus kernel bridge | **SPECIFIED / INERT** | Safety architecture only; no root/sudo capability. |

The fork conformance test deliberately constructs a correctly signed competing
event whose sequence is admissible but whose parent is not the replica’s current
head. This matters: merely editing `prev_event_id` tests envelope-integrity
rejection, not the later competing-head rule.

---

## 4. Architecture

### 4.1 Planes

```text
┌──────────────────────────────── HUMAN COCKPIT ────────────────────────────────┐
│ compact conversation · composer · commentary · evidence · approvals · stop  │
└───────────────────────────────┬──────────────────────────────────────────────┘
                                │ typed requests only
            ┌───────────────────┼──────────────────────┐
            ▼                   ▼                      ▼
     EVIDENCE PLANE       COGNITION PLANE       AUTHORITY PLANE
     records, hashes,     PILOT, WITNESS,        policy, approval,
     receipts, sources    DeepSeek, reviewer     action broker
            │                   │                      │
            │ candidate data    │ proposals only       │ exact capabilities
            └───────────────────┴──────────────────────┘
                                │
                      DETERMINISTIC NEXUS KERNEL
               schemas · reducers · scrubbers · validators
                                │
              ┌─────────────────┼──────────────────┐
              ▼                 ▼                  ▼
         ROOM SPINE       GREYWIRE DROPS      LOOM FORGE
       ordered private    encrypted packets   optional history
          state             and custody        processing
              │                 │                  │
              └─────────────────┼──────────────────┘
                                │ candidate envelopes
                         SAFE ADAPTER GATEWAY
                                │
             application protocols / sources / bearers
```

### 4.2 The metaphor map is functional

The code exposes this vocabulary so product and engineering can share one
language:

| Metaphor | Architecture meaning |
|---|---|
| Lightbulb | One bounded idea, task, or claim made inspectable. |
| Circuit | Typed routes and capability-gated transformations. |
| Fungus | A resilient distributed substrate with no privileged model node. |
| Spore | A small content-addressed work packet that can fork and later rejoin through explicit review. |
| Railway | Ordered stages, switches, receipts, and stop signals. |
| Space | Large context outside the chat plane, addressed rather than injected wholesale. |
| Brain | The room reducer and evidence graph, never a single model. |
| Neuron | A human or agent member emitting signed, bounded events. |

The metaphor must never replace the object model. “The fungus knows” is invalid
provenance; “replicas replayed events 1..N under reducer v1 to root X” is useful.

### 4.3 Hard separation of roles

- **Records** describe what bytes, events, or tool observations existed.
- **Claims** interpret records and may be contested or superseded.
- **Routes** locate records and claims. Routes are disposable and have no
  authority.
- **Models** produce candidate claims, classifications, and action proposals.
- **Deterministic code** validates schemas and state transitions.
- **Humans** choose participation, disclosure, policy, and effects.
- **Connectors** move candidate bytes. They do not grant authority.
- **Bearers** carry bytes. They do not parse application payloads.
- **Observers** retain headers, commitments, or receipts. They need not receive
  plaintext.

---

## 5. Flagship LOOM session pipeline

### 5.1 Operator-facing capture modes

The product must expose exactly these modes:

| Mode | Meaning | External model use | Git proposal |
|---|---|---:|---:|
| `OFF` | No session capture. Factory default. | No | No |
| `LOCAL_ONLY` | Create a local exact-byte record and retain it under the local vault policy. | No | No |
| `GITHUB_REVIEW` | Local capture plus the full approved scrub/review/proposal railway. | Only after explicit scrub/provider approval | Possible, never executed automatically |

**Current truth:** the cockpit persists only `OFF` or `LOCAL_ONLY`; a clean
config defaults to `OFF`. `/loom on` is a visible operator action that creates
or loads a 256-bit archive key through Linux Secret Service.
`nexus_loom_store.py` encrypts each canonical exact-byte record with
ChaCha20-Poly1305, links records by ID, locks the archive across processes,
calls `fsync`, bounds record/archive size, and enforces `0600` file plus `0700`
directory permissions. `/loom off` stops new capture without deleting the
encrypted archive.

External review is blocked until the caller supplies a non-empty
`sealed_archive_ref`; that changes the label to `VERBATIM_LOCAL_SEALED`.
The cockpit obtains that reference only after appending an exact current-session
snapshot to the verified encrypted archive. The Forge module still treats the
reference as caller-supplied metadata; the cockpit/archive composition is the
component that verifies it.

```text
LOOM OFF · NO RECORD
LOOM LOCAL_ONLY · ENCRYPTED HASH-LINKED RECORD · CLOUD BLOCKED
SEALED SNAPSHOT + APPROVED SCRUB HASH · DEEPSEEK ROUTE ELIGIBLE
```

`GITHUB_REVIEW` remains a specified future policy name, not a current persisted
capture mode. The present UI uses an explicit per-session `/forge review`
action and a separate commit-proposal click.

### 5.2 RECORD, CLAIM, ROUTE

The preserved LOOM insight is a three-layer model:

```text
RECORD  immutable source bytes and observations
CLAIM   evidence-classed assertion citing RECORD IDs
ROUTE   disposable navigation derived from records and claims
```

Normative rules:

1. A claim may cite records; it may not cite a route as evidence.
2. A record of a false statement can still be a correct record.
3. A model’s summary is a route or proposal unless explicitly promoted by a
   human-governed claim process.
4. Deleting every route must not destroy source evidence.
5. Git is a persistence and review transport, not truth.

### 5.3 Railway state machine

The implemented Forge stages are:

```text
CAPTURED_LOCAL
  -> SCRUB_REVIEW_REQUIRED
  -> SCRUB_APPROVED
  -> DEEPSEEK_PENDING
  -> DEEPSEEK_RECORDED
  -> SECOND_REVIEW_PENDING
  -> SECOND_REVIEW_RECORDED
  -> VALIDATED | BLOCKED
  -> COMMIT_PROPOSED | KEEP_LOCAL | DISCARDED
```

No stage may be skipped. Every transition receives a digest chained from the
prior receipt.

#### Stage A — exact local capture

**IMPLEMENTED / TESTED**

- Input must be non-empty UTF-8 text.
- Maximum current size is 2 MiB.
- `raw_sha256` is computed over the exact UTF-8 bytes.
- Public snapshots expose metadata, not raw or scrubbed content.
- The record is labelled local-only and authority-none.
- Memory-only captures cannot be approved for external model processing.
- A caller-supplied archive reference is required before the “sealed” label and
  external-review gate become available.

Gaps:

- this is exact text capture, not arbitrary byte-stream capture;
- the durable archive is a separate module, not intrinsic to the Forge object;
- the key is Secret-Service-backed, not hardware-attested;
- no delete receipt, retention timer, selective export, key rotation, or
  recovery package exists;
- `fsync` and truncated-record rejection are implemented, but systematic
  power-cut fault injection is not;
- timestamp input is not itself trusted time.

#### Stage B — deterministic preflight and scrub

**IMPLEMENTED / TESTED**

- known secret patterns are redacted;
- exact operator-specified literal redactions are supported;
- residual recognised secret patterns block the route;
- the scrubbed derivative receives its own SHA-256;
- manual privacy review remains required even after the scanner passes.

Scrubbing is not anonymisation. It cannot prove that names, rare phrases,
third-party confidential facts, screenshots, or inferable identities are safe.
The UI must display both the redaction count and the fact that privacy review is
still open.

#### Stage C — approval bound to exact data and providers

**IMPLEMENTED / TESTED**

Approval requires:

- a non-empty approval reference;
- the exact current `scrubbed_sha256`;
- `deepseek` in the provider-family allowlist;
- at least one different provider family for the second pass.

A changed byte invalidates approval. Provider approval is not reusable standing
authority for another session.

#### Stage D — DeepSeek first external processor

**IMPLEMENTED / TESTED WITH INJECTED CALLER; LIVE PROVIDER UNPROVEN**

The first seat must:

- be nonlocal;
- declare family `deepseek`;
- be in the approved provider-family set;
- receive one user-role-only message, with no hidden system prompt;
- treat the scrubbed session as untrusted data;
- return one JSON object with exactly:
  `record_boundaries`, `tags`, `claims`, `privacy_flags`, and `non_claims`.

`nexus_forge_runtime.py` invokes the app-owned external adapter with the exact
work order and records the return through the Forge validator. The cockpit
checks that DeepSeek is configured and nonlocal before starting. The runtime
ordering is unit-tested with an injected caller; a real DeepSeek request is not
claimed until a credentialed operator run yields a receipt. Ordinary chat
having DeepSeek as a default provider does not substitute for this
provenance-bound Forge pass.

The recorded response must match the exact pending work-order ID and seat.
Duplicate JSON keys are rejected rather than silently accepting a parser’s
last-value-wins behaviour. Returned values are scrubbed before the review
artifact is retained.

#### Stage E — distinct higher-model review

**IMPLEMENTED / TESTED WITH INJECTED CALLER; LIVE PROVIDER UNPROVEN**

The second seat must:

- be nonlocal;
- use a model family different from DeepSeek;
- have a declared capability rank greater than the first seat;
- be explicitly allowlisted for this session;
- independently attack record boundaries, privacy, unsupported claims,
  route-as-evidence errors, and omissions;
- return exactly:
  `corrections`, `missed_risks`, `accepted_items`, `rejected_items`, and
  `non_claims`.

The exact pending work-order ID, provider/model seat, family, and capability
rank are bound across request and return.

“Higher” is currently a declared integer ordering, not a benchmark proof. The
UI must disclose who supplied the ranking and must not describe it as objective
model quality.

#### Stage F — deterministic candidate validation

**IMPLEMENTED / TESTED**

Current checks verify:

- scrub passed and the approved scrub hash is current;
- an approval reference exists;
- the first review is external DeepSeek;
- the second review is external, distinct-family, and higher-ranked;
- the rendered candidate passes the known-secret scan;
- raw bytes are not embedded as a candidate field;
- every included proposal is authority-none.

Model agreement is not a validation check. The two outputs remain `DRAFT`
proposals.

#### Stage G — explicit commit proposal

**IMPLEMENTED / INERT**

A proposal binds:

- session ID;
- bounded repository-relative `.json`, `.jsonl`, or `.md` target path;
- candidate, raw, scrubbed, and both review hashes;
- a human approval reference;
- public/private target status;
- privacy and publication approvals when public.

It has:

```text
contains_raw = false
requires_separate_execution_approval = true
execution_available = false
requested_operations = ["git.add", "git.commit"]
status_authority = "NONE"
```

`execute_commit()` always raises `CommitExecutionUnavailable`.

### 5.4 GitHub as opt-in verbatim history

The phrase “verbatim history” needs two distinct objects:

1. **Local exact record:** exact source bytes, private, encrypted when the future
   vault exists.
2. **GitHub projection:** a deterministic scrubbed derivative containing the
   local record’s hash, not the raw private bytes.

GitHub mode is allowed only when all of these are true:

```text
capture_mode == GITHUB_REVIEW
scrub_approved_for_exact_hash
deepseek_review_recorded
distinct_higher_review_recorded
deterministic_validation_passed
operator_selected_exact_target
if public:
  commons_opt_in
  explicit license
  privacy_review_ref
  publish_approval_ref
```

Even then the output is a proposal. A separate Git adapter must show the exact
diff and ask for execution authority. Push and pull-request creation are further
separate effects.

Raw unsafe content must never be silently rewritten and called verbatim. The
future vault should instead produce a `SEALED_RECORD_MANIFEST` containing the
raw hash, ciphertext hash, encryption suite, key reference, retention policy,
and a statement that the plaintext is not in the public projection.

### 5.5 Suggested Forge schemas

Current metadata is close to:

```json
{
  "schema": "nexus.forge-session/v1",
  "session_id": "session-...",
  "stage": "SCRUB_REVIEW_REQUIRED",
  "raw_sha256": "...",
  "raw_byte_length": 1234,
  "raw_label": "VERBATIM_LOCAL_MEMORY",
  "sealed_archive_ref": "",
  "privacy": "LOCAL_ONLY",
  "scrubbed_sha256": "...",
  "scrub_passed": true,
  "status_authority": "NONE"
}
```

The durable vault should add a separate object rather than overload this one:

```json
{
  "schema": "nexus.sealed-record-manifest/v1",
  "record_id": "rec-...",
  "plaintext_sha256": "...",
  "ciphertext_sha256": "...",
  "cipher": "XCHACHA20-POLY1305-or-reviewed-equivalent",
  "key_ref": "os-keyring-or-hardware-handle",
  "created_at_observed": "...",
  "retention": {"mode": "UNTIL_OPERATOR_DELETE"},
  "public_projection": false,
  "status_authority": "NONE"
}
```

The manifest must never contain the key.

---

## 6. Twin agents and router interaction

### 6.1 Current ordinary-chat twin

The normal cockpit and the LOOM Forge use different two-model patterns. Do not
collapse them.

Current ordinary chat:

```text
operator turn
  -> bounded evidence retrieval/attachment
  -> PILOT direct provider route
  || local lightweight WITNESS commentary runs concurrently
  -> PILOT result buffered when review is enabled
  -> local WITNESS performs bounded post-answer check
  -> if WITNESS is required and fails, answer is withheld
  -> transcript receives the accepted PILOT result
```

- **PILOT** creates the user-facing answer and action proposals.
- **WITNESS** is currently a local Ollama model, defaulting to `qwen3:0.6b`.
- Deterministic host code owns attachment, cancellation, timeouts, target
  eligibility, and effects.
- The WITNESS receives bounded redacted evidence, not secrets, private project
  context, the operator’s optional system prompt, or full conversation history.
- The WITNESS may dissent. It cannot mutate the answer, arm authority, or write
  host state.
- A distinct PILOT is required; the WITNESS model is excluded from PILOT
  candidates.

### 6.2 LOOM’s two external seats

The flagship session railway is different:

```text
DeepSeek external first -> distinct-family nonlocal higher reviewer second
```

The local WITNESS cannot replace either Forge seat. It may inspect deterministic
Forge telemetry or warn about missing stages, but its output does not satisfy
the external provenance constraints.

### 6.3 Typed coordination envelope

`TwinEnvelope` binds:

- unique event ID and turn ID;
- generation;
- sender and recipient from `PILOT`, `WITNESS`, `HOST`;
- semantic kind and class;
- payload hash rather than an implicit mutable object;
- references;
- hop count and hop limit;
- `status_authority=NONE`.

Future room agents should reuse this discipline, not necessarily this exact
class. Agent-to-agent messages must carry:

```text
identity + role + turn/task ID + generation + kind + content hash
+ evidence refs + budget + hop limit + authority NONE
```

### 6.4 Retrieval stays out of chat until attached

Evidence packets support:

- `SYSTEM_GREP`;
- `NEWS_SEARCH`;
- `BROWSER`;
- `FILE`;
- `MANUAL`.

They are parked outside transcript with source locator, excerpt fingerprint,
retrieved/inspected flags, exclusions, errors, and authority-none. The operator
may attach a packet to PILOT, WITNESS, or both. A bounded automatic project grep
may be enabled per policy, but it must be visible and must not include private
roots or credential files.

News search and system grep should therefore affect the **evidence plane**, not
silently rewrite conversation history.

### 6.5 Recursive debugging pipeline

A safe recursive pipeline is:

```text
1. FRAME
   operator request -> bounded task object

2. RETRIEVE
   exact source records -> evidence packets

3. PROPOSE
   PILOT/worker -> patch or diagnostic claim

4. ATTACK
   independent reviewer -> counterexample/omission list

5. VERIFY
   deterministic tests, lint, hashes, runtime probes

6. DECIDE
   host/human -> accept, revise, split, or reject

7. RECORD
   receipt references inputs, diff, tests, and nonclaims

8. RECURSE
   only failed proof obligations become the next task
```

Recursion stops on a passing bounded gate, a fatal contradiction, a budget
limit, repeated low-yield rounds, or human stop. “Run until perfect” is not a
bounded execution policy.

---

## 7. Encrypted room spine

### 7.1 Implemented cryptographic object

The current room uses:

- Ed25519 member identities and signatures;
- a 256-bit symmetric key for one room epoch;
- ChaCha20-Poly1305 authenticated encryption;
- canonical UTF-8 JSON with sorted keys and no insignificant whitespace;
- signed 64-bit integers only; floats are rejected;
- SHA-256 with domain-separated prefixes;
- strict sequence and previous-head binding;
- pre-state and post-state roots;
- a rolling accumulator root;
- policy and reducer-version binding.

Supported decrypted event kinds are:

- `MESSAGE`;
- `CLAIM`;
- `EVIDENCE_NOTE`;
- `TASK_OFFER`;
- `TASK_RESULT`.

### 7.2 Room event

The observer-safe event header contains:

```json
{
  "schema": "nexus.room.event/v1",
  "room_id": "...",
  "sequence": 1,
  "prev_event_id": "...",
  "epoch": 1,
  "sender_id": "...",
  "sender_public_key": "...",
  "message_class": "MESSAGE",
  "policy_sha256": "...",
  "reducer_version": "nexus.room.reducer/v1",
  "pre_state_root": "...",
  "post_state_root": "...",
  "nonce": "...",
  "ciphertext_sha256": "...",
  "event_id": "...",
  "signature": "..."
}
```

Ciphertext is carried separately and omitted from the lightweight header.
Plaintext event bodies do not appear in observer receipts or checkpoints.

### 7.3 Admission order

Replica admission is:

```text
schema/size/canonical envelope
  -> event ID
  -> sender key binding and signature
  -> room and epoch
  -> policy and reducer
  -> next sequence
  -> current previous head
  -> pre-state root
  -> active membership
  -> authenticated decryption
  -> canonical plaintext bytes
  -> message-class match
  -> deterministic reducer
  -> post-state root
  -> commit head and accumulator
```

Failure must leave the old state unchanged.

### 7.4 Deterministic commons policy

The implemented policy is an opt-in technical scheduler, not a political or
economic truth:

- member IDs are unique and sorted;
- membership is epoch-bound and opt-in;
- assignment is round-robin;
- active task capacity is bounded per member;
- hidden administrators are forbidden;
- only the assigned member may submit a task result;
- no model receives an implicit administrator path.

This supplies routine coordination without requiring a human to assign every
task. Humans still establish the epoch, membership, policy, and recovery path.

### 7.5 Observer receipts and checkpoints

An observer receipt says:

```text
observer X signed that it observed envelope E
```

It does not say:

```text
the plaintext is true
the observer decrypted it
every observer has it
the room accepted it
the event is legally final
```

A checkpoint binds room, epoch, sequence, head, state root, accumulator root,
policy hash, reducer version, signer, and reliance scope. Verification requires
the expected policy hash and an allowed signer set.

### 7.6 Room gaps before networking

**SPECIFIED / NOT IMPLEMENTED**

- persistent encrypted event store;
- safe epoch-key distribution;
- member join/leave key rotation;
- revocation and historical authority lookup;
- forward secrecy and post-compromise security;
- device recovery and multi-device membership;
- sequencer election or multi-writer ordering;
- correctly modelled competing signed heads;
- offline fork discovery, resolution, and retained void branches;
- availability policy and observer challenge/reveal;
- transport protocol, retransmission, backpressure, expiry, and deduplication;
- metadata-hiding, cover traffic, or traffic-analysis resistance;
- independent cryptographic review.

The current shared epoch key gives group confidentiality only while that key
remains secret. Any holder can decrypt all captured ciphertext from that epoch.

---

## 8. Greywire Drops and custody

### 8.1 Implemented Drop

A Drop is transport-independent:

```text
plaintext
  -> random content key + ChaCha20-Poly1305
  -> content-addressed ciphertext
  -> ephemeral X25519 exchange with recipient
  -> HKDF-SHA256 wrapping key
  -> wrapped content key
  -> Ed25519-signed lightweight manifest
```

The manifest binds:

- sender signing and encryption keys;
- recipient ID and encryption key;
- media type and sizes;
- payload and wrapping nonces;
- ciphertext, wrapped-key, and Drop hashes;
- ephemeral public key;
- sender signature.

The lightweight manifest intentionally omits ciphertext and wrapped-key bulk
bytes.

### 8.2 Satoshi-like custody

The local `DropCustodyLedger` models one live output:

```text
genesis output owned by Drop sender
  -> current owner signs transfer
  -> consume exactly one known unspent output
  -> create exactly one linked successor
  -> preserve Drop ID and monotonic transfer index
  -> reject reuse of consumed output
```

This is “satoshi-like” only in the narrow UTXO-shaped custody sense. It is not a
cryptocurrency, does not create scarcity for decrypted information, and does
not settle value.

### 8.3 Proof boundary

The Drop layer may establish signed custody transitions and
encrypted-content integrity in one accepted local history. It does not establish:

- that a decrypted copy was deleted;
- that the plaintext is unique or true;
- that the current owner is a legal owner;
- that another ledger did not accept a competing history;
- that the sender’s device or keys were uncompromised;
- that transport metadata remained private.

### 8.4 Room + Drop composition

Use the room for small ordered state and the Drop for bulk/private payloads:

```text
Drop ciphertext -> any approved bearer/storage
Drop manifest   -> room EVIDENCE_NOTE or typed attachment
Custody output  -> room CLAIM under an explicit policy
Observer        -> stores event header/checkpoint and optional ciphertext
```

Do not put large file bytes in the room reducer. Do not let a bearer decide Drop
validity. Do not describe a room note as custody unless the exact custody object
and local ledger validation are referenced.

---

## 9. Safe Nexus kernel adapter

### 9.1 Purpose

The adapter is a narrow membrane between untrusted information sources and the
NEXUS evidence/agent planes. It prevents “connected” from becoming “trusted” or
“authorised.”

### 9.2 Ingress cage

The implemented fixture state machine is:

```text
RECEIVED_UNTRUSTED
  -> LIMITS_VALIDATED
  -> QUARANTINED
  -> SOURCE_SIGNAL_CHECKED
  -> SAFE_DERIVATIVE
  -> POLICY_CLASSIFIED
  -> SCRUBBED
  -> HUMAN_ADMITTED
  -> EVIDENCE_RECORDED
  -> ROUTE_ELIGIBLE
```

Terminal alternatives are:

```text
REJECTED | EXPIRED | DEAD_LETTER
```

Rules:

- type and byte ceiling are validated before parsing;
- payload is isolated from routes, effects, and model context;
- a source signal is labelled but never converted into truth;
- active content and archives are not executed;
- opaque media is represented by hash and metadata, not decoded;
- secret detection fails closed;
- the human admits the exact scrubbed hash;
- an evidence reference is required before routing;
- public snapshots omit raw and derivative content;
- every transition has a deterministic receipt hash and authority-none.

Current code processes only caller-supplied in-memory fixtures. It does not open
network connections or devices.

### 9.3 Egress capability firewall

Every future effect must be represented as an `ActionProposal`, not model prose:

```json
{
  "schema": "nexus.action-proposal/v1",
  "action_id": "...",
  "capability": "github.create_commit",
  "arguments": {"target": "...", "candidate_sha256": "..."},
  "input_refs": ["..."],
  "risk": "HIGH",
  "preview": "...",
  "rollback_claim": "NONE",
  "approval_policy": "HUMAN_ONLY",
  "expires_at": "...",
  "status_authority": "NONE"
}
```

The broker must:

- match a fixed capability ID;
- validate every structured argument;
- show an exact preview/diff;
- require the configured human approval;
- use a non-shell handler;
- enforce time, path, token, and cost bounds;
- emit pre/postcondition receipts;
- stop safely on Pause or expiry.

### 9.4 Privileged host boundary

Privileged actions remain **REJECTED in the current app**.

If a future capability genuinely needs elevation, use a separate root-owned,
small, audited service with fixed methods and polkit authorization. Never pass
model strings to a shell. Never install `NOPASSWD: ALL`. Never make the GUI or
agent permanently root. A model cannot approve, arm, extend, or resume a grant.

---

## 10. Connectivity registry

### 10.1 Layer model

The registry enforces five non-interchangeable layers:

| Layer | Job |
|---|---|
| `APPLICATION_PROTOCOL` | Carries typed application messages or workflow requests. |
| `SOURCE_ADAPTER` | Converts explicitly selected source material into candidate ingress. |
| `BEARER` | Carries bytes only; does not parse or grant application capabilities. |
| `GATEWAY` | Provides an isolation/control boundary; is not an authority. |
| `AUTHORITY_EVIDENCE` | Reports scoped evidence; cannot promote it into settlement or canon. |

All 25 current entries are disabled, credential-free, endpoint-free, non-polling
`INERT_STUB` objects. Only registry inspection and caller-supplied fixture
processing exist.

### 10.2 Connector roadmap

| Connector | Layer | Intended use | Current/future guard |
|---|---|---|---|
| Nostr | Application protocol | Signed event exchange and relay-carried room/Drop references | **INERT.** Signing and publish require human-only effects; relay events remain untrusted. Follow NIP-01/event validation before any live adapter. |
| RoomFinal | Authority/evidence | Import local fixtures/checkpoint propositions | **INERT.** Ingress only; `settle` is forbidden; evidence never becomes consensus. |
| IRC | Application protocol | Low-bandwidth human/agent chat and staged work requests | **INERT.** Authenticate server/session, parse message tags safely, rate-limit, never treat nick as identity. |
| Discord | Application protocol | Explicit bot/app events and work queues | **INERT.** No user-token automation; minimise intents and content access; sending is human-only. |
| Slack | Application protocol | App-scoped events, thread-bound work, review queues | **INERT.** App/event scopes only; no workspace scraping; sending is human-only. |
| WinMX | Application protocol, research-only | Import archival chat fixtures to study resilient room UX | **INERT.** Live networking and downloads forbidden; no revival of unsafe file sharing. |
| BitTorrent | Application protocol, research-only | Inspect opaque manifest/chunk fixtures and design room-scoped encrypted artifact swarms | **INERT.** DHT, PEX, local discovery, rendezvous, downloading and seeding are forbidden; a matching hash does not establish safety, authorship or licence. |
| MediaWiki/Wikipedia | Source adapter | Fetch exact public revisions and park gap-aware provenance outside chat | **INERT.** Fixture ingress only; editing and embedded-content execution are forbidden; revision IDs, hashes and patrol state do not establish truth. |
| GitHub | Application protocol | Issues/PRs as staggered work requests, review bus, optional scrubbed LOOM projections | **INERT.** Commit/push/merge are separate human-approved effects; public repositories are not private channels. |
| RSS/Atom | Source adapter | News and project feeds parked outside chat | **INERT.** Fetch limits, source timestamps, dedupe, and prompt-injection fencing required. |
| Email | Application protocol | Explicit mailbox-to-work-item intake and signed/encrypted envelopes | **INERT.** No broad mailbox crawl; send is human-only; attachments quarantine first. |
| Web search | Source adapter | Bounded current-source retrieval into evidence packets | **INERT registry entry.** Search results are candidates, not inspected truth. |
| Webhook | Application protocol | Authenticated one-way event ingress | **INERT.** Replay window, signature verification, size limits, and dead-letter path required. |
| Greywire Drop | Application protocol | Transport-independent encrypted packet exchange | Local cryptographic object exists; live connector remains **INERT**. |
| Removable media | Source adapter | Explicit offline import/export | **INERT.** Never auto-mount/execute; hash first; write protection and user selection preferred. |
| Codex app server | Application protocol | Typed local tool surface | **INERT.** Private local IPC, explicit tool schemas, no ambient host authority. |
| ChatGPT handoff | Source adapter | Visible review/copy workflow or future typed MCP integration | Local explicit open/copy scaffold only; no DOM scraping or cookie reuse. |
| Browser | Source adapter | User-selected page excerpts and downloads | Local scaffold exists. User-triggered only; activeTab scope; no hidden DOM/session scrape. |
| Voice | Source adapter | Press-to-record transcript drafts | Scaffolded browser draft path. No always-listening microphone; transcript has no command authority. |
| Media | Source adapter | Explicit selected image/audio/video evidence | **INERT fixture path.** Opaque hash-only until a sandboxed codec pipeline exists. |
| Dial-up | Bearer | Low-bandwidth IP or store-and-forward transport | **INERT.** It carries bytes only; application crypto and validity stay above it. |
| Ham radio | Bearer | Future legal, low-rate emergency experiments | **FORBIDDEN transmit in current registry.** No encrypted amateur traffic or PTT control. Regulatory review is mandatory. |
| Starlink | Bearer | Commercial satellite IP access | **INERT.** Treat as ordinary untrusted IP; no Starlink hardware/account control. |
| Hardened OS gateway | Gateway | Separate low-privilege quarantine host | **INERT.** No root/sudo/kernel control; gateway compromise must not confer NEXUS authority. |
| Tails companion gateway | Gateway | Separate companion device/process for reviewed exchange | **INERT.** Do not modify or claim affiliation with Tails; preserve its trust boundary. |

Reference specifications for future contributors:

- Nostr NIPs and NIP-01:
  <https://github.com/nostr-protocol/nips> and
  <https://github.com/nostr-protocol/nips/blob/master/01.md>
- IRCv3 capability negotiation and message tags:
  <https://ircv3.net/specs/extensions/capability-negotiation.html> and
  <https://ircv3.net/specs/extensions/message-tags.html>
- Discord Gateway: <https://docs.discord.com/developers/events/gateway>
- Slack Socket Mode: <https://api.slack.com/apis/connections/socket>
- GitHub App webhooks:
  <https://docs.github.com/en/apps/creating-github-apps/writing-code-for-a-github-app/building-a-github-app-that-responds-to-webhook-events>

Those links are protocol references, not evidence that a connector exists.

### 10.3 Staggered and forked work through GitHub

GitHub can be a slow bus:

```text
room task/claim
  -> scrubbed WorkRequest proposal
  -> issue or draft PR branch
  -> independent agent forks/patches
  -> CI/test receipts
  -> review claims cite exact commits and logs
  -> human merge decision
  -> room records resulting commit as an observation
```

Properties:

- request, branch, patch, review, and merge are different objects;
- a PR is a route/work surface, not canonical truth;
- a public GitHub branch is public;
- secrets and private room raw data never enter issue/PR text;
- each agent works inside a bounded repository and capability set;
- agents may check each other’s work, but neither self-approves effects;
- rejected branches remain referenceable rather than silently rewritten.

---

## 11. Human/agent/P2P workspace

### 11.1 Participants

| Participant | Allowed role | Not allowed |
|---|---|---|
| Human operator | Establish policy, approve disclosure/effects, inspect evidence, stop/recover | Cannot make cryptographic claims true merely by asserting them |
| PILOT | Answer, plan, propose changes, cite evidence | Execute host actions or self-promote claims |
| WITNESS | Retrieve, comment, dissent, check bounded outputs | Rewrite the answer, grant authority, become hidden admin |
| Worker agent | Accept bounded task, produce content-addressed result | Expand repo/host scope without a new proposal |
| Observer | Store signed headers, checkpoints, ciphertext per policy | Infer plaintext truth or settlement |
| Connector | Carry candidate data under a capability contract | Become member, admin, truth source, or effect authority |

### 11.2 Room membership

Membership must be:

- explicit and epoch-bound;
- bound to signing and, where needed, encryption keys;
- visible in the cockpit;
- revocable in a future key-lifecycle state machine;
- incapable of creating a hidden administrator;
- separable from connector login names and model-provider accounts.

### 11.3 Work object

```json
{
  "schema": "nexus.work-request/v1",
  "task_id": "...",
  "room_id": "...",
  "offered_by": "...",
  "objective": "...",
  "input_refs": ["record-or-drop-id"],
  "allowed_repositories": ["owner/repo"],
  "allowed_capabilities": ["read", "patch", "test"],
  "forbidden_capabilities": ["publish", "root", "secrets"],
  "budget": {"tokens": 0, "time_seconds": 0, "cost_minor": 0},
  "acceptance_tests": ["..."],
  "expiry": "...",
  "status_authority": "NONE"
}
```

The room reducer currently stores only task ID, summary, offerer, assignee,
status, and result hash. The richer schema is a future Drop or evidence object,
referenced by hash from the room.

### 11.4 Private continuous room

The safe interpretation of “a room that never stops” is:

- append-only logical continuity;
- resumable local replicas;
- periodic scoped checkpoints;
- observers retaining policy-approved encrypted envelopes or headers;
- explicit liveness and availability status;
- no immortal process, undeletable data, or uninterruptible authority.

Every daemon must still have Pause, Stop, retention, and recovery semantics.

---

## 12. Browser extension boundary

### 12.1 Current scaffold

The Firefox/Chromium organ:

- has `activeTab`, context-menu, native-messaging, and scripting permissions;
- uses no broad host-permission list;
- captures only a user-triggered selection or requested page excerpt;
- accepts a visibly reviewed voice transcript as a draft;
- can return already attached PILOT context for review/copy;
- opens ChatGPT only on explicit operator action;
- stores resulting evidence packets outside chat with authority-none;
- rejects secret-like excerpts and oversized/malformed messages;
- accepts HTTPS, local files, and plain HTTP only on loopback;
- does not collect cookies, hidden DOM, or session state.

### 12.2 Never cross this line

The extension must not:

- scrape all tabs or complete private ChatGPT history;
- automate login, reuse cookies, or bypass site permissions;
- inject a prompt into a composer without a separate reviewed action;
- listen continuously;
- store API keys;
- turn webpage text into executable instructions;
- attach a capture to a model silently;
- navigate, submit forms, download, or publish as an inferred follow-up.

### 12.3 Future typed integration

A production ChatGPT/Codex bridge should expose a few typed, least-privilege
tools:

```text
evidence.list_metadata
evidence.get_scrubbed
evidence.attach
work.propose
room.get_checkpoint
drop.get_manifest
```

There should be no `shell`, `sudo`, `read_all_browser_data`, or
`publish_anywhere` tool.

---

## 13. Cockpit UX specification

### 13.1 Experience contract

The app opens as a tiny useful terminal. Additional machinery unfolds only when
the operator expands the window or opens a deck. Normal conversation contains
only operator and assistant words; telemetry lives in the commentary,
provenance, evidence, and activity surfaces.

The desired feeling is:

- spacecraft rather than website;
- dense but calm;
- high-contrast and terminal-native;
- direct keyboard access;
- no tall empty rectangle;
- no routine modal questionnaires;
- state visible without becoming transcript clutter.

### 13.2 Current visual primitives

| Semantic token | Current value |
|---|---|
| `surface.canvas` | `#05090d` |
| `surface.chrome` | `#09131b` |
| `surface.raised` | `#0d1b24` |
| `surface.conversation` | `#071017` |
| `text.assistant` / `state.ready` | `#58ffb2` |
| `text.muted` / `border.passive` | `#29775d` |
| `text.secondary` | `#a9ffda` |
| `text.operator` | `#d7fff0` |
| `state.active` / `focus.ring` | `#4bdcff` |
| `action.primary` | `#2fffa0` |
| `state.error` / cloud danger | `#ff5577` |
| `state.warning` / explicit approval | `#ffc857` |
| `text.neutral` | `#d7e6ea` |

Risk meaning must use semantic tokens plus a word/icon, never colour alone.

### 13.3 Geometry

Use a 4 px base unit:

```text
4 tight gap
8 control gap
12 panel inset
16 major inset
24 section separation
32 deck separation
```

Targets:

- compact startup: `900x560`;
- compact minimum: approximately `620x420`;
- cockpit reveal: width at least `1080` and height at least `620`;
- top bar: 40–48 px;
- compact safety strip: 24–30 px;
- composer: 72–110 px;
- control height: 28–34 px compact, 32–38 px cockpit;
- square/hard edges, 0–4 px radius;
- one-pixel semantic borders, two pixels only for focus/error/armed state.

### 13.4 Compact layout

```text
┌──────────────────────────────────────────────────────────────────┐
│ ◈ NEXUS  [RUNNING COMMENTARY] [ROOM] [LOOM OFF] [TOP] [PAUSE]  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ OPERATOR                                                         │
│ ...                                                              │
│                                                                  │
│ ASSISTANT                                                        │
│ ...                                                              │
│                                                                  │
├──────────────────────────────────────────────────────────────────┤
│ [SOURCES] [PROVENANCE] [THINKING] [ACTIVITY]                    │
├──────────────────────────────────────────────────────────┬───────┤
│ composer                                                 │ SEND  │
│                                                          │ STOP  │
├──────────────────────────────────────────────────────────┴───────┤
│ TWIN · deepseek/... + qwen... · LOCAL/CTX · LOOM OFF · AUTH OBS │
└──────────────────────────────────────────────────────────────────┘
```

The Room/LOOM deck may open as the current topmost bay, but it should later
support a compact bottom sheet. Opening the deck must not change capture mode.

### 13.5 Commentary strip

The top strip answers “what is the ship doing now?” It never becomes a second
conversation and never displays private content.

Examples:

```text
LOOM OFF · no session bytes retained
SCRUB REVIEW · 3 redactions · cloud route blocked
FORGE PASS 1 · DeepSeek work order prepared · no request sent
FORGE BLOCKED · second family matches first
ROOM REPLAY · seq 42 · roots agree on 2 replicas
DROP SEALED · manifest ready · no bearer selected
CONNECTOR INERT · Nostr fixture scrubbed · admission required
```

### 13.6 State chips

Required chips:

| Chip | States |
|---|---|
| Capture | `OFF`, `LOCAL`, `GITHUB REVIEW` |
| Privacy | `RAW LOCAL`, `SCRUB REVIEW`, `SCRUB APPROVED`, `PUBLIC PROJECTION` |
| Forge | stage enum or `BLOCKED` |
| Room | `LOCAL`, `SYNCING`, `REPLAYED`, `FORK`, `KEY ROTATION`, `DEGRADED` |
| Drop | `SEALED`, `MANIFEST`, `IN TRANSIT`, `OPENED`, `CUSTODY CONTESTED` |
| Twin | PILOT target, WITNESS target, required/optional, review status |
| Authority | `OBSERVE`, `SUGGEST`, future `ACT`; current host must remain non-privileged |
| Connector | `INERT`, future `CONNECTED`, `QUARANTINED`, `ADMITTED`, `ERROR` |

### 13.7 Copy language

Good:

```text
Signed envelope verified
Replay agrees under policy X and reducer Y
Observed by 3 named observers
Scrub scanner clear; privacy review still required
Commit proposal ready; no Git operation occurred
```

Bad:

```text
Message is true
Room is universally final
File cannot be copied
AI approved it
History published safely
Secure because encrypted
```

### 13.8 Artist workflow

A design contributor can alter layout, type, colour primitives, iconography, and
animation if these invariants survive:

1. Capture mode and authority remain visible at compact size.
2. OFF never looks active.
3. Prepared, sent, recorded, validated, proposed, committed, pushed, and
   published are visually distinct states.
4. Raw, scrubbed, model-produced, and human-approved content never share an
   ambiguous label.
5. Warning and failure have textual meaning, not colour alone.
6. Room proof language stays scoped.
7. The composer cursor and answer outrank decoration.
8. Pause and Stop remain reachable.

---

## 14. Threat model

### 14.1 Assets

- API credentials and local signing/decryption keys;
- raw session records and private room plaintext;
- provider/model disclosure approvals;
- room membership and epoch policy;
- ordered event and custody history;
- Git candidate content and approval references;
- operator intent and host authority;
- source provenance and evidence hashes.

### 14.2 Adversaries and failures

| Threat | Present mitigation | Remaining gap |
|---|---|---|
| Prompt injection in web/repo/chat payload | Untrusted-data labels, evidence plane, quarantine stages, no connector effects | Models can still be persuaded; output needs deterministic validation and human review |
| Secret exfiltration to cloud | Known-secret scrub, literal redactions, exact-hash approval, provider allowlist | Heuristic detection is incomplete; privacy inference and provider retention remain |
| Malicious or compromised model | Two roles, distinct Forge family, authority-none, no direct effects | Both providers may fail similarly or be correlated |
| Route becoming truth | RECORD/CLAIM/ROUTE separation, routes authority-none | UI or contributor copy can still launder certainty |
| Event tampering | Event ID, Ed25519 signature, AEAD, ciphertext hash | Device/key compromise remains |
| Replay or out-of-order room event | Strict sequence, previous head, pre/post roots | No distributed fork/election protocol |
| Shared epoch key leaked | Epoch binding | No forward secrecy, rotation, or revocation implementation |
| Observer metadata leakage | Plaintext omitted from headers/receipts | Room ID, timing, sender, class, size, and graph may remain visible |
| Drop ciphertext modified | Content hashes and AEAD | Availability and deletion are unproved |
| Decrypted Drop copied | Explicit nonclaim | Fundamentally not preventable by this protocol |
| Custody double-transfer | Local single-live-output ledger rejects reuse | Another isolated ledger may accept a competing history |
| GitHub data leak | OFF default, scrubbed-only proposal, public opt-in/license/privacy/publish gates | Separate execution adapter not yet built; operator can still intentionally disclose |
| Hidden browser capture | User-triggered activeTab/native host, no broad host list | Browser/extension compromise is out of process scope |
| Microphone surveillance | Press-to-start reviewed transcript design | Production MediaRecorder/STT path not implemented |
| Malicious media/archive | Opaque hash-only fixture; archives/active content forbidden | Sandboxed codec pipeline absent |
| Connector impersonation | Source signal stays non-authoritative | Live authentication adapters absent |
| Root takeover | No root/sudo connector capability; broker only specified | Entire GUI runs in user context and is not a hardened security boundary |
| Supply-chain compromise | Small local modules, hashes, tests | No reproducible build, dependency lock/audit, or independent review yet |
| Radio-law violation | Ham transmit forbidden in registry | Any future experiment needs jurisdiction-specific legal review |
| Tails trust-base damage | Separate companion gateway only | Companion design and formal isolation proof absent |

### 14.3 Security properties that need formal conformance vectors

- canonical encoding across Python and at least one independent implementation;
- signed competing-head and replay vectors;
- epoch transition and revoked-member vectors;
- Drop cross-language seal/open and tamper vectors;
- custody split-brain and reconciliation vectors;
- scrub scanner positive, negative, and evasion corpora;
- Forge stale-hash, same-family, lower-rank, malformed-output, and secret-return
  vectors;
- connector state-machine illegal-transition vectors;
- browser-origin, framing, oversize, secret, and native-host abuse vectors;
- commit proposal path traversal and post-validation mutation vectors.

---

## 15. Contributor implementation roadmap

### Phase 0 — make the local truth green

1. Keep the valid competing signed-head test separate from simple
   envelope-integrity mutation tests.
2. Keep the dedicated `test_nexus_forge.py` green and add integration coverage
   when live provider adapters exist.
3. Freeze schema examples and domain separators as test vectors.
4. Run:

```bash
python3 -B -m unittest -v \
  test_nexus_core.py \
  test_nexus_twin.py \
  test_nexus_room.py \
  test_nexus_drop.py \
  test_nexus_connectors.py \
  test_nexus_forge.py \
  test_nexus_forge_runtime.py \
  test_nexus_loom_store.py \
  test_matrix_terminal.py
```

5. Build both browser variants and run native-host tests.
6. Run Python/JavaScript/shell syntax checks and `git diff --check`.

Exit: clean tests from a fresh checkout with no network and no credentials.

### Phase 1 — durable local LOOM vault

Implemented slice:

- explicit `OFF` / `LOCAL_ONLY` config with factory `OFF`;
- canonical append-only exact-byte record framing;
- ChaCha20-Poly1305 at-rest encryption with a Linux Secret Service key;
- plaintext/ciphertext hashes, record IDs, and prior-record links;
- cross-process file locking, bounded reads/appends, `fsync`, `0600`/`0700`;
- wrong-key, tamper, noncanonical, truncated-record, lost-update, and
  per-session-index tests;
- visible enable/disable/status and per-session Forge privacy review.

Remaining:

- power-cut fault-injection at every write boundary;
- retention, selective export, deletion receipts, key rotation/recovery, and
  hardware-backed key option;
- an independent archive verifier and stable cross-language vectors;
- proof that no plaintext reached swap, crash dumps, screen capture, or a
  compromised session (the current design does not claim this).

Exit: killing the app at every write boundary either recovers a valid record or
an explicit incomplete record; no plaintext remains in logs/config/temp files.

### Phase 2 — Forge adapters

Implemented slice:

- a narrow effect-injected runtime that consumes only `ForgeWorkOrder`
  user-role messages;
- app-owned external DeepSeek-first and separately selected higher-family
  adapter calls;
- exact seat/family/rank return binding and fail-closed structured parsing;
- local models rejected for both Forge seats;
- local preview plus exact scrub-hash/provider-family approval.

Remaining:

- persist provider/model/family/version/capability-rank provenance;
- add token, cost, retry, and timeout budgets;
- never retry by silently changing provider family.
- record and replay sanitized HTTP fixtures for every supported provider;
- perform an explicit credentialed live test without logging prompts or keys.

Exit: recorded HTTP fixtures prove DeepSeek-first and distinct-higher-second;
network failure cannot skip a stage or create a proposal.

### Phase 3 — proposal-only Git bus

- add a bounded Git adapter that accepts only `CommitProposal`;
- show exact candidate diff and target path;
- require a fresh execution approval;
- stage and commit only the exact candidate hash;
- keep push and PR creation as separate proposals;
- record resulting commit hash as an observation, not validation;
- support private-repository policy without claiming public-repo privacy.

Exit: stale candidate, altered path, missing approval, raw content, or public
policy failure blocks before any Git mutation.

### Phase 4 — room persistence and key lifecycle

- encrypted event log and checkpoint store;
- signed membership epochs;
- key distribution/rotation/revocation;
- offline replay and snapshot verification;
- multi-device identities;
- competing signed-head detection and explicit fork UI;
- availability/challenge policy;
- backup/recovery without hidden recovery admin.

Exit: two independent clients pass the same canonical vectors and expose, rather
than silently resolve, incompatible heads.

### Phase 5 — live adapter gateway

Build one ingress-only connector first, preferably RSS/Atom or a signed webhook:

- separate process;
- no credentials in NEXUS config;
- authenticated source where available;
- strict byte/type/rate bounds;
- dead-letter and expiry;
- exact ingress receipts;
- quarantine before model context;
- no egress.

Only after that should duplex chat adapters be considered.

Exit: a hostile fixture corpus cannot execute content, skip admission, authorize
effects, or insert itself into transcript.

### Phase 6 — browser/voice productionisation

- stable Chromium extension ID and Firefox signing;
- reviewed native-host installer;
- explicit capture indicator and per-origin policy;
- browser test automation;
- press-to-record local or short-lived STT flow;
- raw-audio retention OFF by default;
- accessibility and permission-revocation UX.

Exit: store-ready packages, no broad host permission, and no capture without a
fresh user gesture.

### Phase 7 — experimental bearers

Dial-up, satellite IP, removable media, and any legal radio experiment begin as
transport labs. They receive already encrypted, size-bounded packets and never
own application validity.

Ham transmit remains forbidden unless an independently reviewed, lawful,
jurisdiction-specific design changes that boundary. The default research path
is receive-only metadata or simulated fixtures.

---

## 15A. Mutated-quine child workspaces

**Status: AUDITED LINEAGE + SPECIFIED / NOT IMPLEMENTED**

This is a useful flow-state shape, but an executable self-copying HTML file is
not yet a safe child-workspace capsule.

### 15A.1 Existing lineage

The local corpus contains:

- `Nexus_Agent_v0_15_quine_roundtrip_fixed.html`, SHA-256
  `70976a6f9734f3f5688165b2a3f29f060678e6be927f8832cf3c5ad19dfa32fa`;
- Lab `nexus-agent-v0.14-scrubbed.html`, SHA-256
  `b7ff658c45367cceb2b559787deb479ba47e322250eccbb01189eb8c22bd6e8f`,
  imported at Lab commit `761aee6`;
- draft HT-001 language for governed self-modifying lineage;
- NEXUS Lineage v0.1 candidate specification, SHA-256
  `1cb23b6f963782d0d67ed215f55f4c8390e7a18589d9d25981079999e59d905d`;
- current ordinary Git clones/worktrees, which do not yet carry a signed
  child-workspace transition.

The quine already serialises selected browser state, embeds it in its next HTML,
increments a generation, records a parent/mutation summary, and downloads a
child. Those are design ancestors, not cryptographic proof.

### 15A.2 Defects that block promotion

The audit found material, testable faults:

1. v0.14 and v0.15 contain the same lineage comment
   (`generation:2`, `parent:hkrkqky`, `hash:hq7gxeg`) despite different
   full-file SHA-256 values.
2. `simpleHash()` is a non-cryptographic 32-bit rolling hash over only the first
   10,000 characters.
3. Ordinary export and mutation both increment the generation.
4. “Round-trip tests” are presence-checking `stub_pass` placeholders, but UI
   copy can report that all tests passed.
5. Embedded state is unsigned and lacks a canonical import schema.
6. Blacklist-style secret filtering can miss unknown credential/identity
   shapes, while some identity/account namespaces are deliberately exported.
7. Protected-text replacement checks do not stop an additive monkeypatch
   elsewhere from overriding the quine, policy, provider, or evolution code.
8. The HTML child is active executable content with possible network/provider
   paths; an import viewer must treat it as inert bytes until separately
   approved sandbox materialisation.

These findings stick out enough to block reuse of the existing lineage field or
“all tests passed” badge. They do not require changing the current NEXUS app.

### 15A.3 Safe child-workspace flow

```text
RawIntent (authority NONE)
  -> canonical parent WorkspaceSnapshot
  -> reconstructable MutationDelta
  -> signed ChildTransition
  -> narrowed CapabilityEnvelope
  -> encrypted EvidenceCapsule / Greywire Drop
  -> receiver CustodyAcceptance
  -> inert inspection
  -> explicit sandbox materialisation
  -> deterministic ReplayCheckpoint
  -> optional HostAttestation
  -> FINAL_UNDER_NAMED_POLICY only after the declared gate
```

Child keys are newly generated. A child receives selected state, never the
parent private key, provider keys, ambient environment credentials, browser
cookies, or undeclared filesystem authority.

### 15A.4 Required objects

`nexus.workspace.snapshot/v1`

- canonical tree/manifest root;
- file-mode, symlink, Unicode, and path-normalisation policy;
- state-object and dependency-lock roots;
- explicit exclusion manifest and secret-scan receipt;
- runtime/toolchain references, not ambient discovery.

`nexus.workspace.mutation-delta/v1`

- parent and child snapshot IDs;
- ordered patch/object references;
- bound RawIntent/IntentBinding references;
- reasons, scars, and exact reconstruction result;
- export-only operations do not create a generation.

`nexus.workspace.child-transition/v1`

- parent/child IDs, generation, mutation ID;
- new child public key;
- capability-envelope ID;
- nonce, expiry, and parent/operator signatures;
- no self-hash can substitute for an authorised parent transition.

`nexus.workspace.capability-envelope/v1`

- repositories and path scopes;
- read/write/test/network/tool permissions;
- approval labels, budget, expiry, `may_spawn`, and `max_depth`;
- non-delegable secret/root/publish capabilities;
- every child set must be a subset of its parent set.

`nexus.workspace.handoff/v1`

- capsule root and custody output;
- sender/receiver keys and epochs;
- signed offer/accept, nonce, expiry, idempotency key;
- lost acknowledgements replay safely; conflicts become visible evidence.

`nexus.workspace.runtime-measurement/v1`,
`host-attestation/v1`, and `replay-checkpoint/v1`

- bind snapshot, runtime/container/VM measurement, dependency roots, reducer,
  policy, verifier versions, challenge nonce, event head, state root, and gate
  trace;
- host heartbeats expire rather than silently implying continuous presence.

`nexus.workspace.revocation/v1` and `fork-resolution/v1`

- scope and activation boundary;
- reason, replacement, and authority signature;
- competing children remain visible;
- rejected effects may be voided under policy, but rejected bytes are retained.

`nexus.workspace.evidence-capsule/v1`

- complete reachable object closure;
- protocol/verifier hashes and results;
- custody/availability claims and explicit nonclaims;
- transport may be Git, Drop, removable media, Nostr, or another bearer without
  inheriting validity from that bearer.

### 15A.5 Honest “provably hosted” boundary

A signed host statement can prove only that the named host key signed a
nonce-bound claim about a measured snapshot/checkpoint. With stronger hardware
evidence it may additionally prove that a named attestation mechanism reported
a measurement. It does not prove:

- continuous hosting or permanent availability;
- correct external inputs or honest model behaviour;
- deletion of copies;
- absence of hidden forks;
- operator/provider independence;
- that a public hostname served those bytes for the entire claimed interval.

Use orthogonal statuses:

```text
HOST_SIGNED
MEASUREMENT_MATCHED
HARDWARE_ATTESTED
REPLAY_REPRODUCED
HEARTBEAT_STALE
SUSPENDED_HOST_EVIDENCE
```

Never collapse these to an unqualified `PROVABLY_HOSTED`.

### 15A.6 Flow-state mapping

| Object/event | Flow state |
|---|---|
| exact human phrase | `RawIntent`, authority `NONE` |
| operational restatement | `IntentBinding` proposal |
| workspace snapshot | `ORDERED` |
| child/mutation assertion | `CLAIMED` |
| deterministic reconstruction and tests | `VALID` |
| competing head, smell, or dissent | `CHALLENGED` |
| missing object, verifier mismatch, stale host | `SUSPENDED` |
| named gate satisfied | `FINAL_UNDER_<POLICY>` |
| irreducible ambiguity | `UNABLE_TO_RESOLVE` |

### 15A.7 Minimum hostile tests

- full-byte snapshot reproduction across clean machines;
- any tree, delta, policy, exclusion, mode, symlink, or dependency mutation
  changes the relevant ID;
- parent plus delta reconstructs the exact child;
- self-hashed child without signed transition is rejected;
- parent keys and ambient credentials never enter the child;
- capability widening, spawn-depth bypass, expiry bypass, root/network/publish
  addition, and secret-handle delegation fail closed;
- additive monkeypatches outside protected text are detected;
- no `stub_pass` can satisfy promotion or “all tests passed”;
- missing capsule objects suspend instead of guessing;
- concurrent children create visible forks;
- revocation preserves historical signatures and applies only at its boundary;
- nonce replay, host-key substitution, rollback, stale heartbeat, and
  measurement mismatch suspend host evidence;
- imported HTML/capsules perform no network, script, provider, storage, or
  materialisation effect during inspection;
- a child cannot spawn, contact a network, reach parent storage, erase lineage,
  or create generation N+1 without a new authorised transition.

---

## 15B. GunZ latency, lobby, relay, and selection audit

**Status: SOURCE-AUDITED DESIGN INPUT / NO GAME CODE IMPORTED**

Open GunZ is useful here because it makes several normally hidden choices
visible: who decides a result, which historical view is consulted, how a room
role moves, when peers try a direct path, and when a relay is introduced. The
useful transfer is the separation of those concerns. Its combat trust model
must not be copied into a human/agent workspace.

### 15B.1 What the implementation actually separates

The inspected Open GunZ revision exposes three room-scoped netcode modes:
server-based, P2P anti-lead, and P2P lead. The P2P anti-lead path reconstructs a
historical target view around the shot timestamp on the shooter's client and
sends the resulting damage claim. In the observed receive path, the target
client applies a damage message addressed to its local character. That produces
immediate shooter feedback, but the claimant participates in adjudicating its
own claim.

The server-based path instead stores received movement history, estimates a
reconciliation instant using server time and measured sender latency, performs
the historical pick on the server, and applies the result there. This is closer
to an evidence mediator, but it still depends on client-originated observations,
server clock and ping estimates, and a bounded sample buffer rather than a
fully specified cryptographic observation protocol.

The lobby and transport roles are also distinct:

- the first eligible player entering a stage becomes stage master;
- when the master leaves, the server selects the first eligible entry in its
  ordered map, not a random or elected replacement;
- automatic team assignment chooses the smaller team and deterministically
  favours red on a tie;
- Quick Join filters public eligible stages and then uses process-global C
  `rand()` to select one;
- recommended-channel selection walks eligible channels in deterministic order;
- P2P modes attempt direct UDP peer paths and can use a separately assigned
  relay agent when direct reachability fails;
- server-based mode disables the peer mesh for game-state transport;
- the stage master is a room-control role, not automatically the packet relay or
  authoritative combat host.

These policies are inconsistent by modern audit standards: some are stable but
biased, one is pseudo-random and not replayable from a receipt, and none records
a candidate-set commitment explaining why the selected peer or stage won.

### 15B.2 What syncs with NEXUS

Adopt these seams:

1. **Observation is not effect.** Preserve the actor's local observation and
   low-latency preview, then reconcile it against a named historical snapshot
   before it can mutate accepted room state.
2. **History has an explicit budget.** A policy names the maximum look-back,
   clock source, sampling rule, missing-sample behaviour, and late-claim result.
3. **Transport is not authority.** Direct peer delivery may fall back to a
   relay without the relay becoming room master, policy owner, signer, reviewer,
   or result adjudicator.
4. **Roles are leases.** Coordinator, sequencer, reviewer, relay, archive
   observer, and model seats rotate through explicit epochs and handoff
   receipts. Joining first or having the lowest opaque ID grants no permanent
   power.
5. **Room policy selects the reconciliation mode.** A room can choose trusted
   mediator, multi-observer comparison, or local-only preview, but that choice
   is visible in every resulting receipt.
6. **Randomness is an object.** Convenience selection and replay ordering never
   depend on ambient `rand()`, wall-clock seed bits, container iteration order,
   or a platform-specific distribution.

Do not copy:

- shooter/claimant-authoritative effects;
- hidden client timestamps accepted as canonical time;
- retroactive state changes presented as if they happened live;
- “first joined,” lowest-ID, or silent colour/team bias as a fairness rule;
- relay ownership silently conferring policy authority;
- a history count limit masquerading as a specified time window;
- a process-global random generator for security, fairness, assignment, or
  canonical replay.

### 15B.3 Temporal reconciliation objects

`nexus.observation-envelope/v1`

- observation ID, room/scope ID, actor key and actor epoch;
- observation kind and content-addressed payload/evidence reference;
- actor-claimed time, adapter receive time, and ordered admission sequence;
- viewpoint, parent snapshot/head, monotonic nonce, and signature;
- no observation carries effect authority by itself.

`nexus.temporal-acceptance-policy/v1`

- named policy and version;
- trusted clock/ordering source and allowed future skew;
- maximum look-back duration and maximum sample gap;
- interpolation/selection rule with exact arithmetic;
- late, missing, conflicting, or unverifiable outcomes;
- privacy rule for retaining historical views.

`nexus.reconciliation-receipt/v1`

- observation and policy IDs;
- historical snapshot IDs actually consulted;
- verifier/reducer identity and input-root commitment;
- `ACCEPTED`, `REJECTED`, `SUSPENDED`, or `CONFLICTING` result;
- canonical reason code, resulting proposal root, and observer receipts;
- explicit distinction between preview time, admission time, and accepted
  effect sequence.

The minimum lifecycle is:

```text
LOCALLY_OBSERVED
  -> ADMITTED_AS_CLAIM
  -> RECONCILIATION_PENDING
  -> ACCEPTED_AS_PROPOSAL | REJECTED | SUSPENDED | CONFLICTING
  -> APPLIED_UNDER_<NAMED_POLICY>
```

No UI may collapse `LOCALLY_OBSERVED`, `ACCEPTED_AS_PROPOSAL`, and
`APPLIED_UNDER_<NAMED_POLICY>` into one green “verified” state.

### 15B.4 Roles, relays, and deterministic selection

`nexus.room.role-lease/v1`

- room ID, role kind, holder key, lease epoch, start/end sequence and expiry;
- eligibility policy, capability limits, and predecessor lease;
- candidate-set root and selection-policy ID;
- signed handoff, acceptance, timeout, revocation, and replacement evidence;
- an explicit `authority_class`; relay and observer leases default to
  `TRANSPORT_ONLY` and `EVIDENCE_ONLY`.

`nexus.transport.relay-lease/v1`

- endpoint pseudonym, supported bearer, size/rate limits, expiry and route ID;
- ciphertext-only forwarding contract and no payload-decryption key;
- health/availability receipts that cannot sign application state;
- direct-attempt evidence and policy-named fallback cause;
- privacy caveat: a relay can still observe timing, volume, and endpoint
  metadata unless a stronger construction is used.

`nexus.selection-receipt/v1`

- purpose and policy version;
- canonical candidate list or Merkle root plus inclusion evidence;
- eligibility decision for every considered candidate;
- ordered-state root and selection sequence;
- winner and exact tie-break trace.

Default assignment is deterministic:

```text
eligible := canonical_sort(candidates, capability_match, accepted_sequence, candidate_id)
winner   := eligible[0]
```

This is replayable allocation, not a claim of social fairness. If a use case
requires an unpredictable fair draw, it needs a separate
`nexus.entropy-round/v1`: participant commitments, reveal deadline, canonical
combiner, candidate-set commitment, bias/abort rule, and selection proof. A
previous room root alone is deterministic but may be influenceable; an external
beacon alone imports external trust. The receipt must name which construction
was used.

### 15B.5 UX consequence

The cockpit should show three parallel facts without interrupting typing:

```text
LOCAL   observation captured / preview available
ROOM    reconciliation pending / accepted / conflicting
ROUTE   direct / relayed / offline queue, with latency and expiry
```

A result reconciled after its visible moment is labelled as a correction with
the old and new state references. NEXUS must never reproduce anti-lead's
confusing product failure where a user reaches apparent safety and is silently
affected later without a causal receipt.

### 15B.6 Required hostile tests

- forged, future, stale, replayed, and reordered actor timestamps;
- divergent peer clocks and asymmetric latency;
- missing history, sparse samples, interpolation boundaries, and exact expiry;
- claimant-generated effect that lacks an independent reconciliation receipt;
- two reducers given identical history must produce identical result bytes;
- direct-route failure followed by relay fallback cannot change content,
  authority, admission order, or policy;
- relay compromise exposes no plaintext or signing capability;
- master/coordinator departure during pending work produces one visible role
  epoch transition and no hidden administrator;
- equal candidates, candidate withdrawal, stale health evidence, and competing
  selection receipts;
- ambient RNG, iteration order, locale, or wall-clock variation cannot change a
  replayed selection;
- entropy participant withholding follows the declared abort/bias rule;
- correction UX retains both causal states and never reports universal
  finality.

---

## 15C. MMO exchange lessons for an asynchronous work bus

**Status: MECHANISM COMPARISON + PROTOCOL SKETCH / NOT A MONEY MARKET**

The World of Warcraft Auction House and RuneScape Grand Exchange are useful
because they let work be submitted, partially fulfilled, and collected later.
NEXUS should borrow that asynchronous shape, not their operator custody,
economic incentives, hidden matching behaviour, or real-money boundaries.

### 15C.1 Documented mechanisms and uncertainty

World of Warcraft's current design distinguishes two important object classes:

- stackable commodities are listed at a unit price, pooled region-wide, bought
  in arbitrary quantities, and automatically drawn from the lowest available
  listings;
- armour, weapons, and other non-commodity objects remain bound to a narrower
  realm or connected-realm market.

That is a strong analogue for standardized independent work versus a unique
lineage-bearing workspace. Blizzard documents the pool and lowest-price
behaviour, but does not publish a normative equal-price allocation rule. The
often-reported newest-first behaviour is therefore an observation, not a
protocol guarantee to copy.

The WoW Token is a still narrower exchange: a region-wide service supplies one
dynamically adjusted quote, removes bidding, and promises a seller the quoted
gold amount if the listing sells. Its reusable lesson is a time-bounded cost
quote. Its real-money bridge, custody model, and opaque market controller are
explicitly out of scope.

RuneScape's Grand Exchange is closer to a hidden limit-order service. A buy
offer reserves coins; a sell offer reserves items; compatible offers may fill
fully or partially; results and unused reservations are collected later.
Detailed price-time priority and guide-price algorithms are not publicly
specified by Jagex. Maintained documentation says same-price age priority is
loose and empirically observed, not a strict FIFO guarantee. Guide prices are
advisory and can lag executable reality.

Neither research trail provides a verified reason to randomize ordinary
matching. Random host selection and order matching solve different problems
and require different policies.

### 15C.2 NEXUS object classes

`FUNGIBLE`

- independently checkable units with the same declared schema and policy;
- examples: bounded public-news retrieval shards, inert mirror chunks, test
  vectors, or identical stateless compute units;
- partial fulfilment is safe only when a named deterministic reducer can
  combine units without changing their meaning;
- the listing cannot contain secrets or mutable repository authority.

`UNIQUE`

- exact repositories, snapshots, agent children, private messages, Drop
  custody outputs, signed reviews, or lineage-bearing mutations;
- always addressed by content/object ID plus parent and policy;
- never substituted merely because another object has the same label or
  model-generated similarity score;
- remains room/private-scope unless an explicit release transition changes it.

`nexus.work.intent/v1`

- intent ID, scope, actor key/epoch and signature;
- `OFFER` or `REQUEST`, object class, object/schema ID, quantity and reducer;
- capability, privacy, evidence and acceptance policies;
- reservation reference, maximum budget/quote, creation sequence and expiry;
- parent intent for revisions; editing creates a new ID and preserves lineage.

`nexus.work.reservation/v1`

- immutable input snapshot and object closure;
- bounded compute/token/time budget;
- narrowly scoped capability handles, never raw provider keys or root access;
- reserved quantity and concurrent-use rule;
- release, expiry, cancellation and compensation transitions.

`nexus.work.match-receipt/v1`

- matched intent IDs and exact fulfilled quantity;
- matcher/policy version and canonical candidate-set root;
- accepted sequence and complete tie-break trace;
- input/reservation roots and resulting assignment IDs;
- observer receipts and explicit nonclaims.

### 15C.3 Lifecycle and partial fulfilment

```text
OPEN
  -> RESERVED
  -> PARTIALLY_MATCHED | MATCHED
  -> IN_PROGRESS
  -> RESULT_PROPOSED
  -> ACCEPTED_UNDER_<NAMED_POLICY>

OPEN | RESERVED | PARTIALLY_MATCHED | IN_PROGRESS
  -> CANCEL_REQUESTED
  -> CANCELLED | COMPENSATING_EVENT_REQUIRED

any non-terminal state
  -> EXPIRED | SUSPENDED | CHALLENGED
```

Cancellation affects only unaccepted work. Once an accepted event has entered
the ordered room history, cancellation appends a compensating event; it cannot
erase the receipt or pretend the work never occurred.

Partial matches each produce a child assignment and result receipt. Their
reducer must bind:

- the original intent and expected shard set;
- every accepted child result ID;
- missing, duplicate, conflicting, or expired shards;
- canonical merge order and exact reducer version;
- final proposal root and the policy that may accept it.

“Matched,” “completed,” and “accepted under policy” are independent statuses.
None means legally settled, universally true, safe to execute, or authorised to
publish.

### 15C.4 Matching, quotes, and backpressure

The default matcher is inspectable and replayable:

1. filter by scope, privacy, capability, object schema, availability, policy,
   budget and unexpired reservation;
2. sort by the named primary term;
3. break ties with `(accepted_sequence, intent_id)`;
4. emit a receipt containing the candidate-set commitment and every exclusion
   reason;
5. allow an independent higher reviewer to challenge the result without
   silently rewriting it.

A model's relevance, confidence, quality, or predicted cost is a **guide
value**, never execution truth. If used for ranking, the exact model, prompt,
input root, output, expiry, and deterministic fallback are evidence in the
receipt. A DeepSeek or higher-model opinion cannot secretly pick a winner.

Backpressure borrows the useful shape of listing slots, buy limits, and deposits
without inventing a currency:

- per-identity outstanding-intent and concurrency budgets;
- explicit query/search rate limits;
- expiring reservations and idempotent retries;
- bounded repost/revision frequency;
- a disclosed cancellation cost such as lost queue position or consumed
  compute, never an invisible fee;
- a fixed maximum API-spend quote that expires before execution and cannot
  silently expand.

Account or key quotas are not Sybil resistance. Public federation requires a
separate admission/reputation policy; private rooms can bind budgets to their
own membership epochs.

### 15C.5 Cockpit lanes

The exchange is not another chat transcript. It appears as quiet lanes:

```text
INBOX       results ready to inspect or attach
WORK        open / reserved / partial / running / challenged
NEWS        independently refreshed public-information results
SYSTEM      grep and machine evidence, never auto-inserted into chat
LINEAGE     unique workspaces, children, Drops, forks and custody
```

“Collect anywhere” means any authorised cockpit surface can fetch a referenced
artifact; it does not duplicate plaintext into every client. News, grep,
reviews, and agent output notify the commentary strip and remain outside model
chat context until the operator attaches or a named room policy admits them.

Aggregate capacity can be public while counterparty identity and private demand
remain hidden. Hiding names from a public API is privacy minimisation, not
cryptographic anonymity; the matcher and room still need a documented metadata
threat model.

### 15C.6 Explicit rejects and required tests

Reject:

- central custody described as peer-to-peer;
- secret order matching, hidden administrator intervention, or undocumented
  equal-price priority;
- newest-first allocation that rewards cancel/repost churn;
- deleting user artifacts as an “item sink”;
- handing a worker raw secrets, signing keys, repository ownership, or sudo as
  escrow;
- treating a guide price, model score, match, or receipt as truth or settlement;
- public order books that reveal private work, interests, or relationships;
- automatic real-money/token exchange;
- randomising a match merely to make it look fair.

Test:

- reservation prevents double assignment of the same unique mutable object;
- fungible partial results merge byte-identically in independent reducers;
- a unique child cannot be substituted by a similar object;
- identical candidate sets produce the same match and exclusion trace;
- concurrent offers have an explicit admission order and no lost update;
- revision creates a new intent, retains its parent, and cannot jump the queue
  invisibly;
- cancellation, expiry, worker crash, retry, and duplicate result are
  idempotent;
- guide-value staleness cannot change an already signed budget or match;
- private demand is absent from public snapshots and observer receipts;
- no match grants effect, commit, publish, network, secret, or privilege
  authority;
- an accepted partial result remains visible when later work is challenged;
- a compromised matcher can be detected from candidate-set and state-root
  disagreement.

---

## 15D. WinMX, BitTorrent, and Wikipedia adapter synthesis

**Status: TWO NEW INERT STUBS + HISTORICAL/PROTOCOL AUDIT / NO LIVE PEERS**

These systems should not be described as one generic “P2P” connector:

- WinMX is useful history for capability-tiered discovery, hosted chat, and the
  danger of untrusted search advertisements;
- BitTorrent is useful for hash-checked chunk transfer and replaceable sources;
- MediaWiki/Wikipedia is useful for revision lineage, public provenance,
  moderation signals, and gap-aware change feeds.

Each source has a different trust boundary. NEXUS combines their safe seams only
after each adapter has produced the same inert evidence envelope.

### 15D.1 WinMX: historical discovery and hosted rooms

No authoritative Frontcode protocol specification was found. Surviving
community documentation says the WinMX Peer Network used higher-capacity
primary nodes to carry discovery traffic for secondary clients. Primaries
exchanged network traffic with other primaries, while secondaries received
search and room-list results through a primary connection.

Chat rooms were hosted by individual primary users. The host controlled room
topic, message of the day, visibility, limits, and moderation. Historical room
identifiers could derive from host IP/port data. Search/download alternatives
were grouped by a file hash, while fake-result flooding was a known operational
problem.

The safe transfer is narrow:

- a capacity-qualified relay may help discovery or carry encrypted packets;
- relay leases expire and are replaceable;
- search results are advertisements, never evidence of safe or authentic
  content;
- several sources may satisfy a signed content manifest;
- room identity, policy, ordering, membership and moderation remain signed room
  state, not powers inherited by a primary relay or chat host.

Do not implement live WPN compatibility inside the trusted kernel. Do not place
raw IP/port coordinates in a public room ID, room chain, model prompt, or Git
history. Short-lived route hints belong in a locally encrypted routing cache.

### 15D.2 BitTorrent: chunks are not trust

Modern BitTorrent cleanly separates metadata/discovery from piece transfer:
trackers or other discovery mechanisms return peer locations, peers exchange
indexed blocks, and a client announces a completed piece after verifying its
expected hash.

The privacy and admission boundary is load-bearing:

- the distributed hash table maps an infohash to peer network coordinates and
  exposes swarm participation to peers and DHT observers;
- magnet metadata can be fetched from peers and validated against its
  infohash, but the hash says nothing about authorship or safety;
- peer exchange spreads peer addresses and its own specification warns about
  bogus-contact poisoning and victim-address injection;
- a private-torrent flag disables DHT, peer exchange, and local discovery in
  conforming clients, but the specification explicitly says this is incomplete
  access control;
- BitTorrent v2's SHA-256 Merkle construction and path-sanitisation requirements
  are useful implementation precedents;
- signed mutable DHT values are small, public, expiring network values—not a
  secret durable room ledger.

For a private NEXUS room, the admissible future shape is:

```text
signed encrypted room manifest
  -> private authenticated rendezvous
  -> mutually authenticated room peers
  -> optional ciphertext-only relay
  -> hash-checked ciphertext chunks outside the lightweight room chain

room chain
  -> manifest root
  -> custody and availability receipts
  -> policy decisions and challenges
```

Every artifact uses randomized per-artifact authenticated encryption.
Cross-room convergent encryption is rejected because ciphertext or key equality
can leak that two rooms hold the same material. The room chain stays lightweight
by committing to a manifest/root rather than storing bulk chunks.

The new `bittorrent` connector is deliberately an offline opaque-fixture stub.
Manifest import requires a human. DHT, peer exchange, private rendezvous, chunk
receive and seeding are all forbidden until an isolated network adapter and
privacy conformance suite exist.

### 15D.3 Wikipedia/MediaWiki: revision evidence, not truth

A MediaWiki revision carries useful lineage: revision ID, parent revision ID,
page ID, actor reference, timestamp, length, comment/deletion state, minor-edit
flag, and potentially several typed content slots.

Important qualifications:

- an upstream content hash is a content-model value, not necessarily a hash of
  the retrieved serialized bytes and not a publisher signature;
- Recent Changes is a transient index and is normally purged;
- Wikimedia EventStreams is a resumable wake-up stream with limited retention,
  not permanent canonical history;
- resumption across data centres may use timestamps rather than portable exact
  offsets, so duplicate, reordered, and missing events are expected;
- patrol/autopatrol is a moderation signal, not a truth guarantee;
- privileged revision deletion can hide content, comments, or actors, and
  maintenance can remove old revisions;
- Wikipedia content is not guaranteed correct, and reuse has attribution and
  licensing obligations.

The future read path is:

```text
EventStreams hint
  -> fetch exact revision from allowlisted API
  -> bind project + page ID + revision ID + parent ID
  -> retain exact response bytes in the encrypted local evidence store
  -> compute local SHA-256
  -> inert slot-aware extraction
  -> source/license/attribution envelope
  -> quarantine
  -> DeepSeek analysis
  -> distinct higher-model review
  -> proposal only
```

Dedupe on `(origin_project, revision_id)`, not timestamp. Backfill parent gaps
through the revision API. Keep upstream `PATROLLED` and local
`ACCEPTED_UNDER_<POLICY>` as orthogonal axes.

The new `mediawiki` stub can process explicitly supplied text/JSON fixtures. A
future revision fetch is approval-gated and a continuous event stream requires
an explicit always-ask policy. Editing and executing content are forbidden.
Wikitext, templates, Lua, JavaScript, CSS, SVG, HTML, URLs, media and embedded
instructions remain inert data.

### 15D.4 Common adapter objects

`nexus.room.advertisement/v1`

- room ID and membership epoch;
- publisher key, capability summary and expiry;
- sealed relay hints rather than public coordinates;
- directory/invite policy and signature;
- no membership token, decryption key, or join authority in the advertisement.

`nexus.content.manifest/v1`

- manifest version, artifact ID, publisher key/signature and room-policy ID;
- total bytes, chunk size, SHA-256 chunk list or Merkle root;
- randomized encryption envelope and ciphertext/plaintext hash domains;
- sanitized logical paths, media-type claim and exact object closure;
- provenance, licence, retention and redistribution policy.

`nexus.content.chunk-receipt/v1`

- artifact ID, chunk index and expected/observed ciphertext hash;
- source pseudonym, route/relay lease and receive sequence;
- quarantine result and parser/scanner receipt hashes;
- duplicate, missing, corrupt and conflict state;
- no claim that hash-correct content is non-malicious or true.

`nexus.source.wiki-revision/v1`

- origin project/host, page ID/title, revision ID and parent ID;
- slot role and content model;
- upstream content hash plus local exact-response SHA-256;
- actor/revision visibility markers and retrieval sequence/time;
- permanent revision URL, licence, attribution and citation set.

`nexus.source.event-cursor/v1`

- source, stream and schema URI;
- last upstream event ID and last independently fetched revision ID;
- gap/duplicate/reorder state;
- backfill start/end and dedupe-set commitment;
- cursor expiry; a cursor never proves complete history by itself.

`nexus.source.redaction-tombstone/v1`

- source/revision reference and observed visibility transition;
- minimum non-sensitive prior receipt necessary to explain the gap;
- local retention/legal policy and bytes-suppression result;
- propagation stop sequence and operator/policy receipt;
- no public reproduction of hidden data.

### 15D.5 One safe ingress railway

All future remote data follows one pipeline:

```text
REMOTE BYTES
  -> strict byte/rate/type/depth bounds
  -> bounded non-executing parser
  -> path and Unicode normalisation checks
  -> quarantine
  -> hash/signature verification where applicable
  -> isolated content scan
  -> inert normalized evidence
  -> DeepSeek
  -> distinct higher-model review
  -> proposal
  -> explicit user or named-policy approval
  -> narrowly scoped effect
```

Hash/signature failure rejects the claim; success advances only the relevant
byte-integrity or key-authorship axis. Neither model sees peer IP addresses,
credentials, secret invitations, decryption/signing keys, executable
attachments, or direct network/write capabilities.

The adapter process does not parse room-validity objects, and the room reducer
does not open sockets or decode source formats. Crossing that boundary requires
a content-addressed evidence object and an admission receipt.

### 15D.6 Explicit rejects and hostile tests

Reject:

- global room discovery, DHT, peer exchange, local peer discovery, or public
  magnets for private rooms;
- filename, extension, claimed MIME type, search rank, patrol status, revision
  ID, or hash treated as “safe” or “true”;
- a single hosted chat room, primary node, tracker, relay, wiki, or model
  becoming canonical authority;
- peer-supplied instructions crossing the data/instruction fence;
- automatic open, render, template expansion, macro, archive, HTML, SVG, script,
  media codec, or binary execution;
- automatic Wikipedia/GitHub edits or torrent publication;
- silent permanent retention or republication of content later hidden for
  privacy/legal reasons.

Test:

- `../`, absolute, reserved-name, symlink, Unicode-normalisation, case-fold and
  path-collision manifests;
- malformed/noncanonical metadata, decompression bombs and impossible sizes;
- hash-correct malware and forged publisher manifests remain quarantined;
- DHT/PEX/local-discovery/IP leakage stays zero in private mode;
- PEX victim-address injection cannot trigger an outbound connection;
- corrupted, duplicate, mixed-manifest and source-equivocated chunks;
- relay delay, replay, reorder and forgery cannot change accepted room order;
- duplicate, out-of-order and schema-changed EventStreams events;
- retention gaps and missing parents trigger bounded backfill or suspension;
- hidden revisions produce tombstones without leaking removed bytes;
- wikitext/template/prompt injection remains inert through both model stages;
- every outbound edit, upload, seed, publish, or share remains unavailable until
  its dedicated adapter and explicit approval path are independently reviewed.

---

## 16. Contributor rules

### 16.1 Before changing a feature

Write down:

- the object and schema;
- whether it is record, claim, route, policy, or effect;
- exact input and output bytes;
- privacy class;
- authority and approval rule;
- deterministic validation;
- failure/terminal states;
- retention;
- negative conformance tests;
- what the feature explicitly does not prove.

### 16.2 Pull request requirements

Every PR touching Room, Drop, Forge, connectors, browser capture, or authority
must include:

- threat delta;
- schema/state-machine delta;
- tests for success and illegal transitions;
- evidence that secrets do not enter snapshots/logs;
- exact UI copy for proof and failure states;
- no-claims update;
- rollback or migration plan;
- source lineage and license notes.

### 16.3 Review separation

At least one reviewer should attack:

- privacy and secret flow;
- canonical encoding/replay;
- authority escalation;
- UI certainty laundering;
- connector scope;
- recovery and deletion.

A model can prepare this review. A human maintainer owns merge authority.

### 16.4 Never merge these shortcuts

- a `shell=True`, `eval`, or string-command bridge from model output;
- cloud routing before exact scrub approval;
- same-family second Forge review;
- a “safe” flag derived only from model output;
- a public raw-history option;
- automatic push/merge;
- silent browser/microphone capture;
- a shared room key stored in browser local storage;
- observer receipt copy that says “final” without its policy scope;
- live WinMX download;
- radio transmit/PTT;
- an official-looking Tails modification;
- a connector that sets `status_authority` to anything but `NONE`.

---

## 17. Test matrix

| Invariant | Current test evidence | Next proof |
|---|---|---|
| Canonical nested JSON is byte-stable; floats rejected | Room tests pass | Independent implementation vectors |
| Two replicas replay one encrypted event to same state/head/accumulator | Room test passes | Long randomized histories and snapshots |
| Ciphertext/header exclude test plaintext | Room test passes | Memory/log inspection |
| Ciphertext tamper fails closed | Room and Drop tests pass | Cross-language mutation corpus |
| Fork/reference tamper fails closed | Valid re-signed competing-head test and envelope mutation tests pass | Cross-client competing-head vectors |
| Observer has authority-none | Room test passes | Checkpoint/receipt parser in second language |
| Deterministic round-robin/no hidden admin | Room tests pass | Epoch transition and capacity property tests |
| Only Drop recipient decrypts | Drop test passes | Independent seal/open vectors |
| Drop manifest omits bulk bytes | Drop test passes | Size/privacy inspection |
| One custody output cannot be spent twice locally | Drop test passes | Split-ledger conflict vectors |
| All 25 connectors are inert/credential-free | Connector tests pass | Static no-I/O audit |
| Bearers cannot parse fixtures | Connector tests pass | Type-level module separation |
| Fixture pipeline stops before human admission | Connector test passes | Fuzz illegal transitions |
| Secret scrub hides recognised fixture secret | Connector test passes | Evasion corpus and manual-review UX |
| Raw connector content omitted from public snapshot | Connector test passes | Serialization audit |
| GunZ-derived observation/effect and route/authority seams are explicit | Specification objects and hostile vectors documented | Independent temporal-reconciliation implementation |
| Work matching distinguishes fungible from lineage-unique objects | Specification state machine and negative rules documented | Deterministic matcher/reducer vectors |
| BitTorrent and MediaWiki remain offline, read-only/inert stubs | Registry negative tests pass | Isolated adapter threat review before any networking |
| Forge DeepSeek-first/distinct-higher/hash gates | Fifteen Forge tests pass, including memory-only cloud block, exact pending seat, duplicate-key rejection, distinct/higher rules, and deterministic candidates | Live-adapter recorded fixtures |
| Commit execution unavailable | Forge negative test passes; proposal is exact and inert | Separate Git adapter threat review |
| Browser is user-triggered and bounded | Scaffold/test suite exists | Browser integration test and signed package |

---

## 18. Source lineage

Hashes below identify the local inputs inspected for this specification. They
are provenance anchors, not endorsements. Untrusted archives were not executed.

### 18.1 Implemented code observed

| Artifact | SHA-256 observed during drafting | Contribution |
|---|---|---|
| `app/nexus_room.py` | `d9dd52bef44d1ca1cd772423dd8c8710fd7ddab70926d3368b437bd62d5c9f95` | Encrypted ordered room, policy, receipts, checkpoints |
| `app/nexus_drop.py` | `a4a3aa25a6f8d18fe28299850945871307503b35052c9a9aadbb9e162f06419f` | Locally sealed Drops and custody ledger |
| `app/nexus_connectors.py` | `261ca8eed0f84c6a21d2dd489a825fcc5839cf0bcc81fa64630e2aad0f16c7a3` | Twenty-five inert connector declarations and fixture ingress cage |
| `app/nexus_forge.py` | `36d0d554bbfc95bd0d02f20929cd282e156435f15549c463940876ea580b8e5b` | LOOM review railway and commit proposal |
| `app/nexus_twin.py` | `18ff2cef8c7aec5f30dcc7819ac9a2f9bcd29aa27051e554b2f23c4d08eb5800` | Twin envelopes, evidence objects, atomic evidence store |

These hashes may change as the working branch changes. Recompute them for a
release manifest.

### 18.2 LOOM lineage

| Artifact | SHA-256 | Reused idea |
|---|---|---|
| `LOOM_v0_1_SPEC.md` | `33b3c38a814555fa3870356a4c2852b19e39cdaa7c0e6b9eb3c2b7ceb870a378` | RECORD/CLAIM/ROUTE separation; routes have no authority; five-stage adversarial tagging concept |
| `LOOM_MANDATORY_CAPTURE.md` | `18fe539e7db33fac6ee7cfd88002608a8ce45a0f92eda156ccc59084d904bdee` | Capture/private-public distinction and process intent |
| `LOOM_RECORD_001_PACK_GENESIS.md` | `cf2f031d7fb06cff372af46644740613684568b9b987e11ab837db3e1c6e23bb` | Append-only process record and explicit non-events |

The original LOOM material is proposal lineage, not runtime authority. Its own
single-seat origin and tagging-bias experiment warn against treating elaborate
model processing as independent proof.

### 18.3 Greywire lineage

| Artifact | SHA-256 | Reused idea |
|---|---|---|
| `Greywire Whitepaper.md` | `23945bf6bfa01ea4bd352eda5858b63d23186b19c55fc72f9b4d201ed58b8ea7` | Messenger-first signed ledger, group scope, visible forks, transport-independent Drops, offline capsules |
| `Greywire Design Spec.md` | `f9ed29fd77dab0ad3432cfac49907b093828570aacb5d2b2c8651e2552fd4bb1` | Trust dashboard, receipt language, Drop and fork UX |
| `Greywire Tech Spec.md` | `537ae0239c4c7c2100f150c17943a5f588bde7db3ce6de4afa33d7018cb7daf5` | Group-state clarity, recovery and relay-privacy surfaces |
| `NEXUS_WHITEPAPER_v4.1_GREYWIRE_SYNTHESIS.md` | `a6c7b2950f06ae4139a0032d964dc23a207df09b039872b4f51f149fbb8c1798` | NEXUS/Greywire synthesis lineage |
| `GREYWIRE_SPINE_synthesis_R001.md` | `21922474b4edbdec1cfbca4e569a492134268d882340308748c745ec9e4cde0e` | Evidence-versus-settlement seam and lightweight head commitments |

### 18.4 Wallet prototype lineage

The user-supplied wallet archive was treated as untrusted static evidence:

```text
archive SHA-256:
43ef6cbdb1208bd72c4a549c171c6b3ed10850d11f86209e244e83933a95c83e

HTML member SHA-256 recorded by the room implementation:
96311ae3c08e76ee9a0f633ff34d57e5acb4b06af3f8e7d7f600d670f0990ab2
```

No code from the archive was executed or imported. The clean-room lesson was to
replace per-tab/local mutable state and extractable browser keys with explicit
canonical events, identity binding, deterministic replay, and honest proof
boundaries.

### 18.5 Open GunZ implementation lineage

The implementation audit used Open GunZ revision
[`b46e3e119e9be671c4a78edd34c15f951f49c528`](https://github.com/open-gunz/ogz-source/tree/b46e3e119e9be671c4a78edd34c15f951f49c528).
Relevant primary-source paths include:

- [`MMatchStageSetting.h`](https://github.com/open-gunz/ogz-source/blob/b46e3e119e9be671c4a78edd34c15f951f49c528/src/CSCommon/Include/MMatchStageSetting.h)
  for room-scoped server/P2P lead modes;
- [`ZGame.cpp`](https://github.com/open-gunz/ogz-source/blob/b46e3e119e9be671c4a78edd34c15f951f49c528/src/Gunz/ZGame.cpp)
  for client-side historical picking, shot-time seed use, and anti-lead damage
  messages;
- [`MMatchServer.cpp`](https://github.com/open-gunz/ogz-source/blob/b46e3e119e9be671c4a78edd34c15f951f49c528/src/MatchServer/MMatchServer.cpp)
  and
  [`BasicInfoHistory.cpp`](https://github.com/open-gunz/ogz-source/blob/b46e3e119e9be671c4a78edd34c15f951f49c528/src/CSCommon/Source/BasicInfoHistory.cpp)
  for server-side reconciliation and historical-state storage;
- [`MMatchStage.cpp`](https://github.com/open-gunz/ogz-source/blob/b46e3e119e9be671c4a78edd34c15f951f49c528/src/MatchServer/MMatchStage.cpp),
  [`MMatchServer_Stage.cpp`](https://github.com/open-gunz/ogz-source/blob/b46e3e119e9be671c4a78edd34c15f951f49c528/src/MatchServer/MMatchServer_Stage.cpp),
  and
  [`MMatchServer_Channel.cpp`](https://github.com/open-gunz/ogz-source/blob/b46e3e119e9be671c4a78edd34c15f951f49c528/src/MatchServer/MMatchServer_Channel.cpp)
  for stage master, team, Quick Join, and channel selection;
- [`MMatchClient.cpp`](https://github.com/open-gunz/ogz-source/blob/b46e3e119e9be671c4a78edd34c15f951f49c528/src/CSCommon/Source/MMatchClient.cpp)
  and
  [`MMatchServer_Agent.cpp`](https://github.com/open-gunz/ogz-source/blob/b46e3e119e9be671c4a78edd34c15f951f49c528/src/MatchServer/MMatchServer_Agent.cpp)
  for peer probing and relay-agent assignment.

The public
[GunZ anti-lead review](https://gunz-online.net/gunz-the-duel-anti-lead-system-under-review-community-vote-live/)
was used only to cross-check the user-visible delayed-damage problem. The source
tree, not community terminology, controls the implementation claims above. No
GunZ code was copied into NEXUS.

### 18.6 MMO exchange references

Publisher or publisher-authored sources:

- Blizzard,
  [Auction House update preview](https://worldofwarcraft.blizzard.com/en-us/news/23236723/visions-of-nzoth-auction-house-update-preview):
  commodity unit pricing, quantity purchase, lowest-price fulfilment, and
  partial listing consumption;
- Blizzard,
  [region-wide commodities](https://worldofwarcraft.blizzard.com/en-us/news/23833174):
  regional commodity pool while armour and weapons remain realm-scoped;
- Blizzard,
  [Connected Realms](https://worldofwarcraft.blizzard.com/en-us/news/10551009/patch-54-feature-preview-connected-realms):
  connected realms share an Auction House;
- Blizzard,
  [WoW Token](https://worldofwarcraft.blizzard.com/en-us/news/18141101/introducing-the-wow-token):
  dynamic region-wide quote, listing-order qualification, guaranteed seller
  quote on a completed sale, no bidding, and explicit exceptional verification
  delay;
- Jagex,
  [original OSRS Grand Exchange design blog](https://oldschool.runescape.wiki/w/Update%3ADev_Blog%3A_The_Grand_Exchange):
  reserved item/coin inputs, matching, partial completion, and later collection;
- Jagex,
  [Old School RuneScape rules](https://legal.jagex.com/docs/rules/rules-of-old-school-runescape):
  botting, account, and real-world-trading boundaries.

Maintained community references were used for current limits, taxes, and
empirically observed matching details:

- [OSRS Grand Exchange](https://oldschool.runescape.wiki/w/Grand_Exchange);
- [OSRS buying limits](https://oldschool.runescape.wiki/w/Grand_Exchange/Buying_limits);
- [RuneScape Grand Exchange](https://runescape.wiki/w/Grand_Exchange);
- [Jagex's 2026 RuneScape exchange-improvement article preserved on the official
  wiki](https://runescape.wiki/w/Update%3ARoad_to_Restoration_-_Grand_Exchange_Improvements);
- [Warcraft Wiki Auction House](https://warcraft.wiki.gg/wiki/Auction_House).

Observed equal-price priority and undisclosed guide-price behaviour remain
labelled empirical. They are not normative NEXUS inputs.

### 18.7 WinMX, BitTorrent, and MediaWiki references

Historical WinMX/WPN mechanics are based on surviving community documentation,
not a published Frontcode protocol specification:

- [WinMX Peer Network overview](https://www.winmxworld.com/tutorials/what-is-the-winmx-peer-network%28wpn%29.html);
- [WinMX chat-room behaviour](https://www.winmxworld.com/tutorials/winmx_chat.html);
- [WinMX room hosting](https://www.winmxworld.com/tutorials/winmx_hosting.html);
- [WinMX hash-based alternative-source search](https://www.winmxworld.com/tutorials/hash_numbers.html).

These sources are treated as historical observations with known attack and
maintenance limitations. They do not authorise live legacy-network access.

BitTorrent protocol sources:

- [BEP 3](https://www.bittorrent.org/beps/bep_0003.html) for metainfo,
  tracker/peer transfer and piece verification;
- [BEP 5](https://www.bittorrent.org/beps/bep_0005.html) for the distributed
  hash table and peer-coordinate discovery;
- [BEP 9](https://www.bittorrent.org/beps/bep_0009.html) for peer-fetched
  metadata and infohash verification;
- [BEP 11](https://www.bittorrent.org/beps/bep_0011.html) for peer exchange and
  its poisoning/DDoS warnings;
- [BEP 27](https://www.bittorrent.org/beps/bep_0027.html) for private-torrent
  discovery restrictions and their explicit access-control limit;
- [BEP 52](https://www.bittorrent.org/beps/bep_0052.html) for SHA-256 Merkle
  trees and safe path requirements;
- [BEP 44](https://www.bittorrent.org/beps/bep_0044.html) as limited inspiration
  for signed versioned pointers, not as a secret durable ledger.

MediaWiki/Wikimedia sources:

- [revision data model](https://www.mediawiki.org/wiki/Manual:Revision);
- [Revisions API](https://www.mediawiki.org/wiki/API:Revisions);
- [content hash semantics](https://www.mediawiki.org/wiki/Manual:Content_table/en);
- [Recent Changes retention model](https://www.mediawiki.org/wiki/Manual:Recentchanges_table);
- [Wikimedia EventStreams](https://wikitech.wikimedia.org/wiki/Event_Platform/EventStreams_HTTP_Service);
- [RevisionDelete](https://www.mediawiki.org/wiki/Help:RevisionDelete) and
  [permanent old-revision deletion tooling](https://www.mediawiki.org/wiki/Manual:DeleteOldRevisions.php);
- [Wikimedia Terms of Use](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use)
  for reliability, licensing, and attribution boundaries.

The protocol documents support byte-transfer and provenance claims only.
Neither peer availability, a matching hash, a patrol flag, nor an upstream
revision establishes truth, safety, room acceptance, or publication authority.

---

## 19. Release checklist

Do not call this a secure P2P release until all answers are “yes”:

- [ ] Is capture visibly OFF on a clean install?
- [ ] Does enabling capture require a direct operator action?
- [ ] Are exact local records durably encrypted without plaintext temp/log
      residue?
- [ ] Can the operator inspect, export, and delete under a documented retention
      model?
- [ ] Does every cloud route bind the exact scrubbed hash and provider family?
- [ ] Is DeepSeek first and the second model nonlocal, distinct-family, and
      higher-ranked under a disclosed policy?
- [ ] Can neither model commit, push, publish, or grant itself authority?
- [ ] Do all schemas have independent canonical vectors?
- [ ] Are room membership, rotation, revocation, forks, and recovery implemented
      and tested?
- [ ] Does Drop copy explain that decrypted information remains copyable?
- [ ] Are observer/checkpoint claims policy-scoped?
- [ ] Are connector credentials outside the main config and process arguments?
- [ ] Does ingress remain quarantined until exact human admission?
- [ ] Does the extension operate with a fresh user gesture and minimal
      permissions?
- [ ] Are Pause, Stop, and degraded states visible in compact mode?
- [ ] Do accessibility checks cover keyboard, screen reader, contrast, reduced
      motion, and non-colour state labels?
- [ ] Are threat model, test receipts, dependency inventory, and source hashes
      attached to the release?
- [ ] Has an independent reviewer attempted to break privacy, replay,
      capability, and certainty-language boundaries?

---

## 20. Final design principle

The spaceship is not smart because it connects to everything. It is smart
because every connection lands in the right layer:

```text
media becomes candidate bytes
candidate bytes become quarantined records
records support contestable claims
models propose interpretations and work
deterministic code validates narrow transitions
humans govern disclosure and effects
routes remain disposable
receipts remain scoped
```

That is how NEXUS can become broad without becoming ambiently dangerous: local
cryptography for privacy, exact records for memory, multiple models for pressure,
deterministic validators for buildability, and explicit human authority for
consequences.
