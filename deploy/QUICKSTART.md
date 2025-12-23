# Quick Start - MCE Cluster Generator Helm Chart

## 1. Install the Chart

### Development

```bash
helm install mce-api ./deploy -f ./deploy/values-dev.yaml
```

### Production

```bash
# Edit values-prod.yaml first to configure your environment
helm install mce-api ./deploy -f ./deploy/values-prod.yaml
```

### Disconnected/Air-gapped

```bash
# Prerequisites:
# 1. Load image to internal registry
podman load -i mce-cluster-generator-2.0.0.tar
podman tag docker.io/roi12345/mce-cluster-generator:2.0.0 \
  registry.internal.local/mce-cluster-generator:2.0.0
podman push registry.internal.local/mce-cluster-generator:2.0.0

# 2. Install chart
helm install mce-api ./deploy -f ./deploy/values-disconnected.yaml
```

---

## 2. Verify Installation

```bash
# Check pods
kubectl get pods -l app.kubernetes.io/name=mce-cluster-generator

# Check service
kubectl get svc -l app.kubernetes.io/name=mce-cluster-generator

# View logs
kubectl logs -f deployment/mce-api-mce-cluster-generator
```

---

## 3. Access the API

### Port Forward

```bash
kubectl port-forward svc/mce-api-mce-cluster-generator 8000:8000
```

Then open:
- Health: http://localhost:8000/health
- API Docs: http://localhost:8000/docs

---

## 4. Customize Configuration

### Quick Override

```bash
helm install mce-api ./deploy \
  --set config.defaultOcpVersion=4.16 \
  --set config.defaultDnsDomain=cluster.mycompany.com \
  --set config.privateRegistry=registry.mycompany.com
```

### Using Custom Values File

```bash
# Create my-values.yaml
cat > my-values.yaml <<EOF
config:
  defaultOcpVersion: "4.16"
  defaultDnsDomain: "cluster.mycompany.com"
  privateRegistry: "registry.mycompany.com"
  supportedVendors: "cisco,dell"

replicaCount: 3

ingress:
  enabled: true
  hosts:
    - host: mce-api.mycompany.com
      paths:
        - path: /
          pathType: Prefix
EOF

# Install
helm install mce-api ./deploy -f my-values.yaml
```

---

## 5. Upgrade

```bash
# Upgrade to new version
helm upgrade mce-api ./deploy \
  --set image.tag=2.1.0 \
  --reuse-values

# Change configuration
helm upgrade mce-api ./deploy \
  -f my-values.yaml
```

---

## 6. Uninstall

```bash
# Remove the release
helm uninstall mce-api

# Remove PVC (if persistence was enabled)
kubectl delete pvc mce-api-mce-cluster-generator-logs
```

---

## Common Use Cases

### Scale Up/Down

```bash
helm upgrade mce-api ./deploy \
  --set replicaCount=5 \
  --reuse-values
```

### Enable Autoscaling

```bash
helm upgrade mce-api ./deploy \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=10 \
  --reuse-values
```

### Enable Ingress

```bash
helm upgrade mce-api ./deploy \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=mce-api.company.com \
  --reuse-values
```

### Change Log Level

```bash
helm upgrade mce-api ./deploy \
  --set config.logLevel=DEBUG \
  --reuse-values
```

---

## Troubleshooting

### Pods Not Starting

```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Check Chart Values

```bash
helm get values mce-api
```

### Test Template Rendering

```bash
helm template mce-api ./deploy -f ./deploy/values-prod.yaml
```

---

## Next Steps

- See [README.md](README.md) for complete documentation
- See [values.yaml](values.yaml) for all configuration options
- See [values-prod.yaml](values-prod.yaml) for production example
- See [values-disconnected.yaml](values-disconnected.yaml) for air-gapped setup
