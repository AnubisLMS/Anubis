{{/*
Expand the name of the chart.
*/}}
{{- define "chart.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "chart.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "chart.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "chart.labels" -}}
{{- if .Values.tag | quote }}git.tag: {{ .Values.tag | quote }}{{- end }}
helm.sh/chart: {{ include "chart.chart" . | quote }}
{{ include "chart.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service | quote }}
heritage: {{ .Release.Service | quote }}
release: {{ .Release.Name | quote }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "chart.selectorLabels" -}}
{{- if .Values.tag | quote }}git.tag: {{ .Values.tag | quote }}{{- end }}
app.kubernetes.io/name: {{ include "chart.name" . | quote }}
app.kubernetes.io/instance: {{ .Release.Name | quote }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "chart.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "chart.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
API env
*/}}
{{- define "api.env" }}
- name: "PYTHONPATH"
  value: "/opt/app"
- name: "MPLCONFIGDIR"
  value: "/tmp"
- name: "DEBUG"
  value: {{- if .Values.debug }} "1"{{- else }} "0"{{- end }}
- name: "MIGRATE"
  value: "0"
- name: "DISABLE_ELK"
  value: "0"
- name: "DOMAIN"
  value: "{{ .Values.domain }}"
- name: "GITHUB_TOKEN"
  valueFrom:
    secretKeyRef:
      name: git
      key: token
- name: "SECRET_KEY"
  valueFrom:
    secretKeyRef:
      name: api
      key: secret-key
- name: "OAUTH_NYU_CONSUMER_KEY"
  valueFrom:
    secretKeyRef:
      name: oauth
      key: nyu-consumer-key
- name: "OAUTH_NYU_CONSUMER_SECRET"
  valueFrom:
    secretKeyRef:
      name: oauth
      key: nyu-consumer-secret
- name: "OAUTH_GITHUB_CONSUMER_KEY"
  valueFrom:
    secretKeyRef:
      name: oauth
      key: github-consumer-key
- name: "OAUTH_GITHUB_CONSUMER_SECRET"
  valueFrom:
    secretKeyRef:
      name: oauth
      key: github-consumer-secret
- name: "DATABASE_URI"
  valueFrom:
    secretKeyRef:
      name: api
      key: database-uri
- name: "DB_PASSWORD"
  valueFrom:
    secretKeyRef:
      name: api
      key: database-password
- name: "DB_HOST"
  valueFrom:
    secretKeyRef:
      name: api
      key: database-host
- name: "DB_PORT"
  valueFrom:
    secretKeyRef:
      name: api
      key: database-port
- name: "REDIS_PASS"
  valueFrom:
    secretKeyRef:
      name: api
      key: redis-password
- name: "SENTRY_DSN"
  valueFrom:
    secretKeyRef:
      name: api
      key: sentry-dsn
- name: "IMAGE_PULL_POLICY"
  value: {{ $.Values.imagePullPolicy | quote }}
{{- end }}