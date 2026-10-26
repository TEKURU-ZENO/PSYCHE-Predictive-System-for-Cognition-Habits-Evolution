export const API_BASE = (typeof process !== "undefined" && process.env.NEXT_PUBLIC_API_URL ? process.env.NEXT_PUBLIC_API_URL : "http://localhost:8000") + "/api/v1";

function getHeaders() {
  const token = typeof window !== 'undefined' ? localStorage.getItem("token") : null;
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {})
  };
}

export async function login(data: any) {
  return fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function register(data: any) {
  return fetch(`${API_BASE}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function getMe() {
  return fetch(`${API_BASE}/auth/me`, {
    method: "GET",
    headers: getHeaders(),
  });
}

export async function logMood(data: any) {
  return fetch(`${API_BASE}/mood/log`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
}

export async function getCurrentState() {
  return fetch(`${API_BASE}/state/current`, {
    method: "GET",
    headers: getHeaders(),
  });
}

export async function logBehavior(data: any) {
  return fetch(`${API_BASE}/behavior/log`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify(data),
  });
}

export async function analyzeText(text: string) {
  return fetch(`${API_BASE}/cognition/analyze`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({text: text}),
  });
}

export async function getMoodPrediction() {
  return fetch(`${API_BASE}/predict/mood`, {
    method: "GET",
    headers: getHeaders(),
  });
}

export async function getRisk() {
  return fetch(`${API_BASE}/predict/risk`, {
    method: "GET",
    headers: getHeaders(),
  });
}

export async function trackAgentOutcome(success: boolean, delta: number = 0, scenario?: string, decision?: string) {
  return fetch(`${API_BASE}/agent/outcome`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ success, delta, scenario, decision }),
  });
}

export async function simulateScenario(scenario: string) {
  return fetch(`${API_BASE}/predict/simulate`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ scenario }),
  });
}

export async function simulateAgentPipeline(scenario: string) {
  return fetch(`${API_BASE}/agent/respond`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ scenario }),
  });
}

export async function sendFeedback(state_key: string, action: string, rating: number) {
  return fetch(`${API_BASE}/intervention/feedback`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ state_key, action, rating }),
  });
}

export async function getPlaybook() {
  return fetch(`${API_BASE}/intervention/playbook`, {
    method: "GET",
    headers: getHeaders(),
  });
}

export async function getMetaProfile() {
  return fetch(`${API_BASE}/meta/profile`, {
    method: "GET",
    headers: getHeaders(),
  });
}

export async function getTelemetry() {
  return fetch(`${API_BASE}/meta/telemetry`, {
    method: "GET",
    headers: getHeaders(),
  });
}

export async function getEvolutionDashboard() {
  return fetch(`${API_BASE}/evolution/dashboard`, {
    method: "GET",
    headers: getHeaders(),
  });
}

export async function getEpisodicMemories(limit: number = 20) {
  return fetch(`${API_BASE}/memory/episodes?limit=${limit}`, {
    method: "GET",
    headers: getHeaders(),
  });
}

export async function getAssociativeGraph() {
  return fetch(`${API_BASE}/memory/graph`, {
    method: "GET",
    headers: getHeaders(),
  });
}

export async function getConsolidatedSchemas() {
  return fetch(`${API_BASE}/memory/schemas`, {
    method: "GET",
    headers: getHeaders(),
  });
}

export async function queryRetrospective(question: string) {
  return fetch(`${API_BASE}/memory/retrospective`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ question }),
  });
}

export async function triggerConsolidation() {
  return fetch(`${API_BASE}/memory/consolidate`, {
    method: "POST",
    headers: getHeaders(),
  });
}

export async function getAmbientStatus() {
  return fetch(`${API_BASE}/proactive/status`, {
    method: "GET",
    headers: getHeaders(),
  });
}

export async function triggerAmbientScan() {
  return fetch(`${API_BASE}/proactive/scan`, {
    method: "POST",
    headers: getHeaders(),
  });
}

export async function acknowledgeAlert(alertId: number) {
  return fetch(`${API_BASE}/proactive/acknowledge/${alertId}`, {
    method: "POST",
    headers: getHeaders(),
  });
}

export async function simulateCounterfactual(scenario: string, current_emotion?: string, current_intensity?: number) {
  return fetch(`${API_BASE}/counterfactual/simulate`, {
    method: "POST",
    headers: getHeaders(),
    body: JSON.stringify({ scenario, current_emotion, current_intensity }),
  });
}

export async function getCounterfactualHistory() {
  return fetch(`${API_BASE}/counterfactual/history`, {
    method: "GET",
    headers: getHeaders(),
  });
}

export async function getPostMortemReports(limit: number = 10) {
  return fetch(`${API_BASE}/post_mortem/reports?limit=${limit}`, {
    method: "GET",
    headers: getHeaders(),
  });
}

export async function getRedTeamAudits(limit: number = 10) {
  return fetch(`${API_BASE}/post_mortem/red_team_audits?limit=${limit}`, {
    method: "GET",
    headers: getHeaders(),
  });
}

export async function getReplayTimeline(limit: number = 15) {
  return fetch(`${API_BASE}/replay/timeline?limit=${limit}`, {
    method: "GET",
    headers: getHeaders(),
  });
}

export async function replayDecision(decisionHash: string) {
  return fetch(`${API_BASE}/replay/decision/${decisionHash}`, {
    method: "GET",
    headers: getHeaders(),
  });
}

export async function exportPrivacyVault() {
  return fetch(`${API_BASE}/vault/export`, {
    method: "GET",
    headers: getHeaders(),
  });
}

export async function purgeMemoryEpisode(episodeId: number) {
  return fetch(`${API_BASE}/vault/memory/${episodeId}`, {
    method: "DELETE",
    headers: getHeaders(),
  });
}

export function getDeliberationStreamUrl(scenario: string): string {
  return `${API_BASE}/agent/stream?scenario=${encodeURIComponent(scenario)}`;
}
