# MCE Cluster Generator - Deployment Checklist

This checklist ensures a successful deployment of the MCE Cluster Generator to Kubernetes/OpenShift.

---

## Pre-Deployment Checklist

### 1. Infrastructure Requirements

- [ ] Kubernetes cluster version 1.19+ or OpenShift 4.x+
- [ ] Helm 3.0+ installed on your workstation
- [ ] kubectl/oc CLI configured and authenticated
- [ ] Sufficient cluster resources:
  - [ ] At least 500m CPU available
  - [ ] At least 512Mi memory available
  - [ ] Storage class available for PVC (if persistence enabled)

### 2. Image Preparation

- [ ] Build Docker/Podman image:
  ```bash
  podman build -t docker.io/roi12345/mce-cluster-generator:2.0.0 .
  ```

- [ ] Test image locally:
  ```bash
  podman run -p 8000:8000 docker.io/roi12345/mce-cluster-generator:2.0.0
  curl http://localhost:8000/health
  ```

- [ ] Push to registry:
  ```bash
  # For public registry
  podman push docker.io/roi12345/mce-cluster-generator:2.0.0

  # For private/disconnected registry
  podman tag docker.io/roi12345/mce-cluster-generator:2.0.0 registry.company.com/mce-cluster-generator:2.0.0
  podman push registry.company.com/mce-cluster-generator:2.0.0
  ```

### 3. Configuration Preparation

- [ ] Review and customize `values.yaml` or create custom values file
- [ ] Set correct DNS domain: `config.defaultDnsDomain`
- [ ] Set private registry URL: `config.privateRegistry`
- [ ] Configure supported vendors: `config.supportedVendors`
- [ ] Configure supported OCP versions: `config.supportedVersions`
- [ ] Set available sites: `config.availableSites`

### 4. Helm Chart Validation

- [ ] Run validation script:
  ```bash
  ./scripts/validate-deployment.sh
  ```

- [ ] Validate chart manually:
  ```bash
  helm lint ./deploy
  helm template test-release ./deploy
  ```

### 5. Security Configuration

- [ ] Review security contexts in `values.yaml`
- [ ] Ensure `runAsNonRoot: true` is set
- [ ] Verify `allowPrivilegeEscalation: false`
- [ ] Configure image pull secrets (if using private registry):
  ```bash
  kubectl create secret docker-registry registry-secret \
    --docker-server=registry.company.com \
    --docker-username=<user> \
    --docker-password=<pass>
  ```

---

## Deployment Steps

### Step 1: Create Namespace (Optional)

```bash
kubectl create namespace mce-api
kubectl config set-context --current --namespace=mce-api
```

### Step 2: Install Helm Chart

#### Option A: Development Environment
```bash
helm install mce-api ./deploy -f ./deploy/values-dev.yaml
```

#### Option B: Production Environment
```bash
helm install mce-api ./deploy -f ./deploy/values-prod.yaml \
  --set config.defaultDnsDomain=cluster.company.com \
  --set config.privateRegistry=registry.company.com
```

#### Option C: Disconnected/Air-gapped Environment
```bash
helm install mce-api ./deploy -f ./deploy/values-disconnected.yaml \
  --set image.repository=registry.internal.local/mce-cluster-generator \
  --set config.privateRegistry=registry.internal.local \
  --set imagePullSecrets[0].name=registry-secret
```

### Step 3: Verify Deployment

- [ ] Check deployment status:
  ```bash
  kubectl get deployments
  kubectl get pods
  kubectl get svc
  kubectl get pvc
  ```

- [ ] Wait for pod to be ready:
  ```bash
  kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=mce-cluster-generator --timeout=300s
  ```

- [ ] Check pod logs:
  ```bash
  kubectl logs -f deployment/mce-api-mce-cluster-generator
  ```

### Step 4: Health Check

- [ ] Port forward to service:
  ```bash
  kubectl port-forward svc/mce-api-mce-cluster-generator 8000:8000
  ```

- [ ] Test health endpoint:
  ```bash
  curl http://localhost:8000/health
  ```

- [ ] Expected response:
  ```json
  {
    "status": "healthy",
    "version": "2.0.0",
    "uptime_seconds": 10
  }
  ```

### Step 5: API Testing

- [ ] Access API documentation:
  ```
  http://localhost:8000/docs
  ```

- [ ] Test defaults endpoint:
  ```bash
  curl http://localhost:8000/api/v1/clusters/defaults
  ```

- [ ] Test vendors endpoint:
  ```bash
  curl http://localhost:8000/api/v1/clusters/vendors
  ```

- [ ] Test flavors endpoint:
  ```bash
  curl http://localhost:8000/api/v1/clusters/flavors
  ```

---

## Post-Deployment Configuration

### 1. Ingress Setup (Optional)

If using ingress:

```bash
helm upgrade mce-api ./deploy \
  --reuse-values \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=mce-api.company.com \
  --set ingress.hosts[0].paths[0].path=/ \
  --set ingress.hosts[0].paths[0].pathType=Prefix
```

Test ingress:
```bash
curl http://mce-api.company.com/health
```

### 2. TLS/SSL Configuration

Create TLS secret:
```bash
kubectl create secret tls mce-api-tls \
  --cert=path/to/cert.pem \
  --key=path/to/key.pem
```

Update ingress:
```bash
helm upgrade mce-api ./deploy \
  --reuse-values \
  --set ingress.tls[0].secretName=mce-api-tls \
  --set ingress.tls[0].hosts[0]=mce-api.company.com
```

### 3. Autoscaling Setup

Enable HPA:
```bash
helm upgrade mce-api ./deploy \
  --reuse-values \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=5 \
  --set autoscaling.targetCPUUtilizationPercentage=70
```

Verify HPA:
```bash
kubectl get hpa
```

### 4. Resource Optimization

Monitor resource usage:
```bash
kubectl top pods
```

Adjust resources if needed:
```bash
helm upgrade mce-api ./deploy \
  --reuse-values \
  --set resources.requests.cpu=1000m \
  --set resources.requests.memory=1Gi \
  --set resources.limits.cpu=2000m \
  --set resources.limits.memory=2Gi
```

---

## Monitoring & Validation

### 1. Health Monitoring

- [ ] Verify liveness probe is working:
  ```bash
  kubectl describe pod <pod-name> | grep -A 5 "Liveness"
  ```

- [ ] Verify readiness probe is working:
  ```bash
  kubectl describe pod <pod-name> | grep -A 5 "Readiness"
  ```

### 2. Log Monitoring

- [ ] View application logs:
  ```bash
  kubectl logs -f deployment/mce-api-mce-cluster-generator
  ```

- [ ] Check for errors:
  ```bash
  kubectl logs deployment/mce-api-mce-cluster-generator | grep -i error
  ```

### 3. Persistent Storage Validation

If persistence is enabled:

- [ ] Check PVC status:
  ```bash
  kubectl get pvc
  ```

- [ ] Verify logs are being written:
  ```bash
  kubectl exec -it deployment/mce-api-mce-cluster-generator -- ls -la /app/logs
  ```

### 4. Network Connectivity

- [ ] Test service DNS resolution:
  ```bash
  kubectl run test-pod --rm -it --image=busybox --restart=Never -- \
    nslookup mce-api-mce-cluster-generator
  ```

- [ ] Test service connectivity:
  ```bash
  kubectl run test-pod --rm -it --image=curlimages/curl --restart=Never -- \
    curl http://mce-api-mce-cluster-generator:8000/health
  ```

---

## Production Readiness Checklist

### High Availability

- [ ] Multiple replicas configured (minimum 2):
  ```bash
  helm upgrade mce-api ./deploy --reuse-values --set replicaCount=3
  ```

- [ ] Pod disruption budget created (optional):
  ```yaml
  apiVersion: policy/v1
  kind: PodDisruptionBudget
  metadata:
    name: mce-api-pdb
  spec:
    minAvailable: 1
    selector:
      matchLabels:
        app.kubernetes.io/name: mce-cluster-generator
  ```

### Security Hardening

- [ ] Security contexts properly configured
- [ ] Network policies applied (if required)
- [ ] RBAC permissions reviewed
- [ ] Secrets externalized (not in values.yaml)
- [ ] Image vulnerability scanning completed

### Backup & Recovery

- [ ] PVC backup strategy defined
- [ ] Configuration backup stored
- [ ] Disaster recovery plan documented

### Documentation

- [ ] Deployment parameters documented
- [ ] Access URLs documented
- [ ] Troubleshooting procedures documented
- [ ] Rollback procedures documented

---

## Rollback Procedures

### Quick Rollback

If deployment fails:

```bash
# Rollback to previous release
helm rollback mce-api

# Or rollback to specific revision
helm rollback mce-api <revision-number>
```

### Check Release History

```bash
helm history mce-api
```

---

## Troubleshooting

### Issue: Pod not starting

**Check:**
```bash
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

**Common causes:**
- Image pull errors → Check image name and pull secrets
- Resource constraints → Check cluster resources
- Configuration errors → Validate values.yaml

### Issue: Health check failing

**Check:**
```bash
kubectl port-forward svc/mce-api-mce-cluster-generator 8000:8000
curl http://localhost:8000/health
```

**Common causes:**
- Application not ready → Increase initialDelaySeconds
- Port mismatch → Verify container port matches service port
- Application crash → Check logs for errors

### Issue: PVC pending

**Check:**
```bash
kubectl get pvc
kubectl describe pvc mce-api-mce-cluster-generator-logs
```

**Solutions:**
- No storage class → Disable persistence or specify storage class
- No available PVs → Create PV or use dynamic provisioning

---

## Success Criteria

Deployment is successful when:

- [ ] ✅ All pods are in `Running` state
- [ ] ✅ All containers are `Ready`
- [ ] ✅ Health endpoint returns HTTP 200
- [ ] ✅ API documentation is accessible
- [ ] ✅ All API endpoints respond correctly
- [ ] ✅ Logs show no errors
- [ ] ✅ PVC is bound (if persistence enabled)
- [ ] ✅ Ingress is accessible (if configured)
- [ ] ✅ Application can generate cluster configs

---

## Additional Resources

- **Helm Chart README**: `deploy/README.md`
- **Quick Start Guide**: `deploy/QUICKSTART.md`
- **API Documentation**: `http://<service-url>/docs`
- **Main README**: `README.md`

---

## Support Contacts

For deployment issues:
1. Check application logs
2. Review Kubernetes events
3. Consult troubleshooting section
4. Contact platform team

---

**Last Updated**: 2025-12-23
**Chart Version**: 2.0.0
**App Version**: 2.0.0
