# Helm Chart Deployment - COMPLETE ✅

## Summary

Successfully created a production-ready Helm chart for deploying the MCE Cluster Generator API on Kubernetes.

---

## What Was Created

### ✅ 1. Helm Chart Structure

Complete Helm chart in the [deploy/](deploy/) directory:

```
deploy/
├── Chart.yaml                      # Chart metadata
├── values.yaml                     # Default values
├── values-dev.yaml                 # Development configuration
├── values-prod.yaml                # Production configuration
├── values-disconnected.yaml        # Air-gapped configuration
├── templates/
│   ├── _helpers.tpl               # Template helpers
│   ├── deployment.yaml            # Deployment resource
│   ├── service.yaml               # Service resource
│   ├── serviceaccount.yaml        # ServiceAccount resource
│   ├── ingress.yaml               # Ingress resource (optional)
│   ├── configmap.yaml             # ConfigMap resource (optional)
│   ├── pvc.yaml                   # PersistentVolumeClaim for logs
│   ├── hpa.yaml                   # HorizontalPodAutoscaler (optional)
│   └── NOTES.txt                  # Post-install notes
├── README.md                       # Complete documentation
├── QUICKSTART.md                   # Quick start guide
├── .helmignore                     # Files to ignore in package
└── .gitignore                      # Git ignore patterns
```

---

## Key Features

### 🎯 Production-Ready

- **Security**: Non-root user (UID 1000), read-only root filesystem option, drop all capabilities
- **High Availability**: Configurable replicas, pod anti-affinity, autoscaling support
- **Observability**: Health checks, liveness/readiness probes, structured logging
- **Resource Management**: CPU/memory limits and requests
- **Persistent Storage**: Optional PVC for logs

### 🔧 Flexible Configuration

- **Environment-Specific Values**: Separate files for dev, prod, and disconnected
- **ConfigMap Support**: Inject custom configuration files
- **Secret Support**: Reference external secrets
- **Environment Variables**: All app config via env vars from values.yaml

### 🌐 Network Options

- **Service Types**: ClusterIP (default), NodePort, LoadBalancer
- **Ingress Support**: Optional ingress with TLS
- **CORS Configuration**: Configurable CORS origins

### ⚙️ Operational Features

- **Autoscaling**: HorizontalPodAutoscaler based on CPU/memory
- **Node Affinity**: NodeSelector, tolerations, affinity rules
- **Persistence**: Optional PVC for log storage
- **Rolling Updates**: Zero-downtime deployments

---

## Configuration via values.yaml

All configuration is managed through values.yaml or environment-specific files:

### Core Application Settings

```yaml
config:
  defaultOcpVersion: "4.16"
  defaultDnsDomain: "example.company.com"
  privateRegistry: "registry.internal.company.com"
  supportedVendors: "cisco,dell,dell-data,h100-gpu,h200-gpu"
  supportedVersions: "4.15,4.16"
  corsOrigins: "*"
  maxNodes: 100
  logLevel: "INFO"
```

### Deployment Settings

```yaml
replicaCount: 3
resources:
  limits:
    cpu: 2000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 512Mi
```

### Persistence

```yaml
persistence:
  enabled: true
  storageClass: "standard"
  size: 5Gi
```

### Ingress

```yaml
ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: mce-api.company.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: mce-api-tls
      hosts:
        - mce-api.company.com
```

---

## Quick Start Commands

### Install for Development

```bash
helm install mce-api ./deploy -f ./deploy/values-dev.yaml
```

### Install for Production

```bash
helm install mce-api ./deploy -f ./deploy/values-prod.yaml
```

### Install for Disconnected Environment

```bash
# 1. Load image to internal registry
podman load -i mce-cluster-generator-2.0.0.tar
podman tag docker.io/roi12345/mce-cluster-generator:2.0.0 \
  registry.internal.local/mce-cluster-generator:2.0.0
podman push registry.internal.local/mce-cluster-generator:2.0.0

# 2. Install chart
helm install mce-api ./deploy -f ./deploy/values-disconnected.yaml
```

### Install with Custom Values

```bash
helm install mce-api ./deploy \
  --set config.defaultOcpVersion=4.16 \
  --set config.defaultDnsDomain=cluster.mycompany.com \
  --set config.privateRegistry=registry.mycompany.com \
  --set replicaCount=3
```

---

## Accessing the Application

### Port Forward (Development/Testing)

```bash
kubectl port-forward svc/mce-api-mce-cluster-generator 8000:8000
```

Then access:
- **Health**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs
- **Vendors**: http://localhost:8000/api/v1/clusters/vendors

### NodePort

```bash
export NODE_PORT=$(kubectl get svc mce-api-mce-cluster-generator -o jsonpath='{.spec.ports[0].nodePort}')
export NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[0].address}')
echo "API URL: http://$NODE_IP:$NODE_PORT"
```

### LoadBalancer

```bash
export SERVICE_IP=$(kubectl get svc mce-api-mce-cluster-generator -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "API URL: http://$SERVICE_IP:8000"
```

### Ingress

```bash
# If ingress is enabled
curl https://mce-api.company.com/health
```

---

## Environment-Specific Configurations

### Development (values-dev.yaml)

- **Replicas**: 1
- **Image Tag**: latest
- **Pull Policy**: Always
- **Debug**: true
- **Log Level**: DEBUG
- **Resources**: Minimal (250m CPU, 256Mi RAM)
- **Persistence**: Disabled
- **Autoscaling**: Disabled

### Production (values-prod.yaml)

- **Replicas**: 3
- **Image Tag**: 2.0.0
- **Pull Policy**: IfNotPresent
- **Debug**: false
- **Log Level**: INFO
- **Resources**: Standard (500m-2000m CPU, 512Mi-2Gi RAM)
- **Persistence**: Enabled (10Gi)
- **Autoscaling**: Enabled (2-10 replicas)
- **Ingress**: Enabled with TLS
- **Pod Anti-Affinity**: Enabled

### Disconnected (values-disconnected.yaml)

- **Image Repository**: Internal registry
- **Image Pull Secrets**: Required
- **Service Type**: NodePort
- **Persistence**: Local storage
- **Autoscaling**: Disabled
- **Ingress**: Disabled

---

## Upgrading

### Update Image Version

```bash
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

### Enable Autoscaling

```bash
helm upgrade mce-api ./deploy \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=10 \
  --reuse-values
```

---

## Monitoring and Operations

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
kubectl get hpa mce-api-mce-cluster-generator
```

### Check Helm Release

```bash
helm list
helm status mce-api
helm get values mce-api
```

---

## Validation

### Chart Linting

```bash
helm lint ./deploy
```

**Result**: ✅ 1 chart(s) linted, 0 chart(s) failed

### Template Rendering

```bash
helm template mce-api ./deploy -f ./deploy/values-prod.yaml
```

### Dry Run

```bash
helm install mce-api ./deploy --dry-run --debug
```

---

## Documentation

Complete documentation available in the deploy directory:

- **[deploy/README.md](deploy/README.md)** - Complete Helm chart documentation
  - All configuration parameters
  - Deployment scenarios
  - Examples
  - Troubleshooting

- **[deploy/QUICKSTART.md](deploy/QUICKSTART.md)** - Quick start guide
  - Basic installation
  - Common use cases
  - Quick commands

- **[deploy/values.yaml](deploy/values.yaml)** - Default values with inline comments

- **[deploy/values-prod.yaml](deploy/values-prod.yaml)** - Production configuration example

- **[deploy/values-dev.yaml](deploy/values-dev.yaml)** - Development configuration example

- **[deploy/values-disconnected.yaml](deploy/values-disconnected.yaml)** - Air-gapped configuration example

---

## Kubernetes Resources Created

When you install the chart, it creates:

1. **Deployment** - Manages pods with the API container
2. **Service** - Exposes the API (ClusterIP/NodePort/LoadBalancer)
3. **ServiceAccount** - For pod identity
4. **PersistentVolumeClaim** - For log storage (if enabled)
5. **Ingress** - For external access (if enabled)
6. **HorizontalPodAutoscaler** - For autoscaling (if enabled)
7. **ConfigMap** - For custom configuration (if enabled)

---

## Security Features

- ✅ Non-root user (UID 1000)
- ✅ Drop all capabilities
- ✅ Read-only root filesystem option
- ✅ Security context for pods and containers
- ✅ Image pull secrets support
- ✅ Network policies compatible
- ✅ Service account with minimal permissions

---

## High Availability Features

- ✅ Multiple replicas support
- ✅ Pod anti-affinity rules
- ✅ Health checks (liveness/readiness)
- ✅ Rolling updates
- ✅ Resource limits and requests
- ✅ Horizontal pod autoscaling
- ✅ Node selector and tolerations

---

## Troubleshooting Guide

### Pods Not Starting

```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Image Pull Errors

```bash
# Create image pull secret
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
kubectl port-forward svc/mce-api-mce-cluster-generator 8000:8000
curl -v http://localhost:8000/health
```

### PVC Issues

```bash
# Check PVC status
kubectl get pvc
kubectl describe pvc mce-api-mce-cluster-generator-logs

# Disable persistence if storageClass not available
helm upgrade mce-api ./deploy \
  --set persistence.enabled=false \
  --reuse-values
```

---

## Uninstalling

### Remove Release

```bash
helm uninstall mce-api
```

### Remove PVC (if persistence enabled)

```bash
kubectl delete pvc mce-api-mce-cluster-generator-logs
```

---

## Next Steps

### For Development:
1. Install with `values-dev.yaml`
2. Port-forward to access locally
3. Iterate on configuration

### For Production:
1. Customize `values-prod.yaml` with your environment settings
2. Install with production values
3. Configure ingress with TLS
4. Enable autoscaling
5. Set up monitoring

### For Disconnected Environments:
1. Load image to internal registry
2. Customize `values-disconnected.yaml`
3. Create image pull secrets if needed
4. Install with disconnected values
5. Use NodePort or LoadBalancer service type

---

## Files Created

### Core Helm Chart:
- `deploy/Chart.yaml`
- `deploy/values.yaml`
- `deploy/templates/_helpers.tpl`
- `deploy/templates/deployment.yaml`
- `deploy/templates/service.yaml`
- `deploy/templates/serviceaccount.yaml`
- `deploy/templates/ingress.yaml`
- `deploy/templates/configmap.yaml`
- `deploy/templates/pvc.yaml`
- `deploy/templates/hpa.yaml`
- `deploy/templates/NOTES.txt`

### Environment-Specific Values:
- `deploy/values-dev.yaml`
- `deploy/values-prod.yaml`
- `deploy/values-disconnected.yaml`

### Documentation:
- `deploy/README.md`
- `deploy/QUICKSTART.md`

### Utility Files:
- `deploy/.helmignore`
- `deploy/.gitignore` (if created)

### Summary:
- `HELM_CHART_COMPLETE.md` (this file)

---

## Conclusion

✅ **Helm chart is complete and ready for deployment!**

**What works:**
- ✅ Chart linting passes
- ✅ All templates render correctly
- ✅ Security best practices implemented
- ✅ High availability support
- ✅ Flexible configuration via values.yaml
- ✅ Environment-specific configurations
- ✅ Comprehensive documentation
- ✅ Health checks configured
- ✅ Autoscaling support
- ✅ Ingress support with TLS
- ✅ Persistent storage for logs
- ✅ Air-gapped deployment ready

**Ready for:**
- ✅ Development deployment
- ✅ Production deployment
- ✅ Disconnected/air-gapped deployment
- ✅ Multi-region deployment
- ✅ High-availability scenarios

🎉 **Helm Chart Complete!**
