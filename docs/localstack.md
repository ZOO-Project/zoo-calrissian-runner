# LocalStack auth token

The integration tests (`tests/test_s2_*.py`) stage results out to S3. Both CI
and local development use [LocalStack](https://www.localstack.cloud/) as the
S3-compatible endpoint instead of real AWS. LocalStack requires a
`LOCALSTACK_AUTH_TOKEN` even for the community image; ZOO-Project has a free
license for open-source projects that covers this.

**The token itself must never be committed to this repository** (not in a
values file, not in `.env`, not in a workflow). It's only ever stored as a
secret, one layer removed from any file git tracks.

## CI (GitHub Actions)

1. Get the token from the ZOO-Project LocalStack account
   (<https://app.localstack.cloud/> > workspace > Auth Tokens). Ask a
   maintainer for access if you don't have it.
2. In the repo, go to **Settings > Secrets and variables > Actions > New
   repository secret**, name it `LOCALSTACK_AUTH_TOKEN`, and paste the token
   there. GitHub encrypts it and redacts it from all logs.
3. Nothing else to do: `.github/workflows/build-and-test.yml` reads
   `${{ secrets.LOCALSTACK_AUTH_TOKEN }}` and materializes it as a
   Kubernetes Secret (`localstack-auth`, in the `eoap-zoo-project`
   namespace) for the duration of the job. `.github/ci/localstack-values.yaml`
   pulls it into the LocalStack pod via `envFrom.secretRef`.

To rotate the token, just update the repository secret - the next CI run
picks it up automatically.

## Local development

Against your own local cluster (e.g. minikube), create the Kubernetes Secret
yourself, once, in whichever terminal you use to type the token - never
through an AI assistant or anywhere it could end up logged:

```bash
kubectl create namespace eoap-zoo-project --dry-run=client -o yaml | kubectl apply -f -
kubectl create secret generic localstack-auth \
  --namespace eoap-zoo-project \
  --from-literal=LOCALSTACK_AUTH_TOKEN=<your token>
```

Then deploy (or upgrade) the LocalStack release with the same
`envFrom.secretRef` LocalStack requires:

```bash
helm repo add localstack https://helm.localstack.cloud
helm upgrade --install eoap-zoo-project-localstack localstack/localstack \
  --version 0.7.0 \
  --namespace eoap-zoo-project \
  --values .github/ci/localstack-values.yaml
```
