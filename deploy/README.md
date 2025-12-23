# MCE Cluster Generator - Helm Chart

This Helm chart deploys the MCE Cluster Generator API on Kubernetes.

---

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- PV provisioner support in the underlying infrastructure (for persistent logs)

---

## Quick Start

### 1. Install with Default Values

```bash
helm install mce-api ./deploy
```

### 2. Install with Custom Values

```bash
# Development
helm install mce-api ./deploy -f ./deploy/values-dev.yaml

# Production
helm install mce-api ./deploy -f ./deploy/values-prod.yaml

# Disconnected/Air-gapped
helm install mce-api ./deploy -f ./deploy/values-disconnected.yaml
```

### 3. Upgrade

```bash
helm upgrade mce-api ./deploy -f ./deploy/values-prod.yaml
```

### 4. Uninstall

```bash
helm uninstall mce-api
```

---

## Configuration

### Using values.yaml

Edit [values.yaml](values.yaml) or create your own values file:

```yaml
config:
  defaultOcpVersion: "4.16"
  defaultDnsDomain: "cluster.company.com"
  privateRegistry: "registry.company.com"
  supportedVendors: "cisco,dell,dell-data,h100-gpu,h200-gpu"
```

### Using --set

```bash
helm install mce-api ./deploy \
  --set config.defaultOcpVersion=4.16 \
  --set config.defaultDnsDomain=cluster.company.com \
  --set config.privateRegistry=registry.company.com \
  --set replicaCount=3
```

### Using --values

```bash
# Create custom-values.yaml
cat > custom-values.yaml <<EOF
config:
  defaultOcpVersion: "4.16"
  defaultDnsDomain: "cluster.mycompany.com"
  privateRegistry: "registry.mycompany.com"

replicaCount: 3

ingress:
  enabled: true
  hosts:
    - host: mce-api.mycompany.com
      paths:
        - path: /
          pathType: Prefix
EOF

helm install mce-api ./deploy -f custom-values.yaml
```

---

## Configuration Parameters

### Image Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `image.repository` | Image repository | `docker.io/roi12345/mce-cluster-generator` |
| `image.tag` | Image tag | `2.0.0` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `imagePullSecrets` | Image pull secrets | `[]` |

### Application Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `config.host` | Server bind address | `0.0.0.0` |
| `config.port` | Server port | `8000` |
| `config.debug` | Enable debug mode | `false` |
| `config.logLevel` | Logging level | `INFO` |
| `config.defaultOcpVersion` | Default OpenShift version | `4.16` |
| `config.defaultDnsDomain` | Default DNS domain | `example.company.com` |
| `config.privateRegistry` | Private container registry | `registry.internal.company.com` |
| `config.supportedVendors` | Comma-separated vendor list | `cisco,dell,dell-data,h100-gpu,h200-gpu` |
| `config.supportedVersions` | Comma-separated version list | `4.15,4.16` |
| `config.corsOrigins` | CORS origins | `*` |
| `config.maxNodes` | Maximum nodes per cluster | `100` |

### Deployment Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `podAnnotations` | Pod annotations | `{}` |
| `podSecurityContext` | Pod security context | See [values.yaml](values.yaml) |
| `securityContext` | Container security context | See [values.yaml](values.yaml) |

### Service Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `8000` |
| `service.annotations` | Service annotations | `{}` |

### Ingress Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress | `false` |
| `ingress.className` | Ingress class name | `""` |
| `ingress.annotations` | Ingress annotations | `{}` |
| `ingress.hosts` | Ingress hosts | See [values.yaml](values.yaml) |
| `ingress.tls` | Ingress TLS configuration | `[]` |

### Persistence Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `persistence.enabled` | Enable persistent storage for logs | `true` |
| `persistence.storageClass` | Storage class | `""` |
| `persistence.accessMode` | Access mode | `ReadWriteOnce` |
| `persistence.size` | Storage size | `5Gi` |

### Resource Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `resources.limits.cpu` | CPU limit | `2000m` |
| `resources.limits.memory` | Memory limit | `2Gi` |
| `resources.requests.cpu` | CPU request | `500m` |
| `resources.requests.memory` | Memory request | `512Mi` |

### Autoscaling Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `autoscaling.enabled` | Enable autoscaling | `false` |
| `autoscaling.minReplicas` | Minimum replicas | `1` |
| `autoscaling.maxReplicas` | Maximum replicas | `10` |
| `autoscaling.targetCPUUtilizationPercentage` | Target CPU utilization | `80` |

---

## Examples

### Example 1: Basic Installation

```bash
helm install mce-api ./deploy
```

### Example 2: Production with Ingress

```bash
helm install mce-api ./deploy \
  --set replicaCount=3 \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=mce-api.company.com \
  --set config.defaultDnsDomain=cluster.company.com \
  --set config.privateRegistry=registry.company.com
```

### Example 3: Disconnected Environment

```bash
# 1. Load image to internal registry first
podman tag docker.io/roi12345/mce-cluster-generator:2.0.0 \
  registry.internal.local/mce-cluster-generator:2.0.0
podman push registry.internal.local/mce-cluster-generator:2.0.0

# 2. Install with disconnected values
helm install mce-api ./deploy -f ./deploy/values-disconnected.yaml
```

### Example 4: Development with Debug Enabled

```bash
helm install mce-api-dev ./deploy -f ./deploy/values-dev.yaml \
  --set config.debug=true \
  --set config.logLevel=DEBUG
```

### Example 5: Using External ConfigMap

```bash
# Create ConfigMap with custom config
kubectl create configmap mce-custom-config --from-file=config.yaml

# Install with ConfigMap reference
helm install mce-api ./deploy \
  --set configMap.enabled=true \
  --set envFrom[0].configMapRef.name=mce-custom-config
```

---

## Deployment Scenarios

### Scenario 1: Standard Kubernetes Cluster

```bash
helm install mce-api ./deploy \
  -f ./deploy/values-prod.yaml \
  --set config.defaultDnsDomain=cluster.example.com \
  --set config.privateRegistry=registry.example.com
```

### Scenario 2: OpenShift Cluster

```bash
helm install mce-api ./deploy \
  --set service.type=Route \
  --set config.defaultDnsDomain=apps.openshift.example.com
```

### Scenario 3: Air-gapped Environment

```bash
# Prerequisites:
# - Image pre-loaded to internal registry
# - Internal registry accessible

helm install mce-api ./deploy \
  -f ./deploy/values-disconnected.yaml \
  --set image.repository=registry.internal.local/mce-cluster-generator \
  --set config.privateRegistry=registry.internal.local
```

### Scenario 4: Multi-Region with NodeSelector

```bash
helm install mce-api ./deploy \
  --set nodeSelector."topology\.kubernetes\.io/zone"=us-east-1a \
  --set replicaCount=2
```

---

## Accessing the Application

### Port Forward (Development)

```bash
export POD_NAME=$(kubectl get pods -l "app.kubernetes.io/name=mce-cluster-generator" -o jsonpath="{.items[0].metadata.name}")
kubectl port-forward $POD_NAME 8000:8000
```

Then access:
- Health: http://localhost:8000/health
- API Docs: http://localhost:8000/docs

### NodePort

```bash
export NODE_PORT=$(kubectl get svc mce-api-mce-cluster-generator -o jsonpath='{.spec.ports[0].nodePort}')
export NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[0].address}')
echo http://$NODE_IP:$NODE_PORT
```

### LoadBalancer

```bash
export SERVICE_IP=$(kubectl get svc mce-api-mce-cluster-generator -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo http://$SERVICE_IP:8000
```

### Ingress

```bash
# If ingress is enabled
curl http://mce-api.company.com/health
```

---

## Monitoring

### Check Pod Status

```bash
kubectl get pods -l app.kubernetes.io/name=mce-cluster-generator
```

### View Logs

```bash
kubectl logs -f deployment/mce-api-mce-cluster-generator
```

### Check Health

```bash
kubectl port-forward svc/mce-api-mce-cluster-generator 8000:8000 &
curl http://localhost:8000/health
```

### Describe Resources

```bash
kubectl describe deployment mce-api-mce-cluster-generator
kubectl describe svc mce-api-mce-cluster-generator
kubectl describe pvc mce-api-mce-cluster-generator-logs
```

---

## Upgrading

### Upgrade to New Version

```bash
# Update image tag in values
helm upgrade mce-api ./deploy \
  --set image.tag=2.1.0 \
  --reuse-values
```

### Change Configuration

```bash
helm upgrade mce-api ./deploy \
  --set config.defaultOcpVersion=4.17 \
  --reuse-values
```

### Scale Replicas

```bash
helm upgrade mce-api ./deploy \
  --set replicaCount=5 \
  --reuse-values
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -l app.kubernetes.io/name=mce-cluster-generator

# Describe pod
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>
```

### Image Pull Errors

```bash
# For disconnected environments, ensure image is in internal registry
# Create image pull secret if needed
kubectl create secret docker-registry internal-registry-secret \
  --docker-server=registry.internal.local \
  --docker-username=<username> \
  --docker-password=<password>

# Update values
helm upgrade mce-api ./deploy \
  --set imagePullSecrets[0].name=internal-registry-secret \
  --reuse-values
```

### Health Check Failing

```bash
# Check if service is running
kubectl get svc

# Port forward and test
kubectl port-forward svc/mce-api-mce-cluster-generator 8000:8000
curl http://localhost:8000/health
```

### PVC Issues

```bash
# Check PVC status
kubectl get pvc

# Describe PVC
kubectl describe pvc mce-api-mce-cluster-generator-logs

# If storageClass not available, disable persistence
helm upgrade mce-api ./deploy \
  --set persistence.enabled=false \
  --reuse-values
```

---

## Uninstalling

### Delete Release

```bash
helm uninstall mce-api
```

### Delete PVC (if persistence enabled)

```bash
kubectl delete pvc mce-api-mce-cluster-generator-logs
```

---

## Advanced Configuration

### Using External Secrets

```bash
# Create secret
kubectl create secret generic mce-api-secrets \
  --from-literal=PRIVATE_REGISTRY=registry.company.com \
  --from-literal=API_KEY=xyz123

# Reference in helm
helm install mce-api ./deploy \
  --set envFrom[0].secretRef.name=mce-api-secrets
```

### Custom Health Check Configuration

```bash
helm install mce-api ./deploy \
  --set livenessProbe.initialDelaySeconds=60 \
  --set readinessProbe.initialDelaySeconds=30
```

### Network Policies

Create a NetworkPolicy for the deployment:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: mce-api-netpol
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: mce-cluster-generator
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: default
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 443  # For registry access
```

---

## Chart Development

### Linting

```bash
helm lint ./deploy
```

### Template Rendering

```bash
helm template mce-api ./deploy
```

### Dry Run

```bash
helm install mce-api ./deploy --dry-run --debug
```

### Package Chart

```bash
helm package ./deploy
```

---

## Support

For issues or questions:
- View pod logs: `kubectl logs -f deployment/mce-api-mce-cluster-generator`
- Check pod events: `kubectl describe pod <pod-name>`
- API documentation: `http://<service-url>/docs`
