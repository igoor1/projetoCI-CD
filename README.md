![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/fastapi-%23009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%232496ED.svg?style=for-the-badge&logo=docker&logoColor=white)
![Rancher](https://img.shields.io/badge/rancher-%230075A8.svg?style=for-the-badge&logo=rancher&logoColor=white)
![Kubernetes](https://img.shields.io/badge/kubernetes-%23326CE5.svg?style=for-the-badge&logo=kubernetes&logoColor=white)
![ArgoCD](https://img.shields.io/badge/ArgoCD-%23EF7422.svg?style=for-the-badge&logo=argo&logoColor=white)

# Pipeline CI/CD com GitHub Actions e GitOps

## Visão geral

Este documento descreve o pipeline de integração e entrega continua (CI/CD) para a API Python. O processo é baseado em GitOp, utilizando dois repositórios distintos:

1. Repositório da Aplicação(app-repo): Contém o código-fonte da API Python e o workflow de CI.

2. Repositório de Manifestos(manifest-repo): Contém os manifestos Kubernetes (YAMLs) e serve como a "fonte da verdade" para o ArgoCD.

O objetivo é que, quando um desenvolvedor enviar um novo código para o `app-repo`, o pipeline deva automaticamente construir uma nova versão da imagem, atualizar o `manifest-repo`, e o ArgoCD cuidará da implantação(deploy) no cluster.

## Repositórios Relacionados

* **Manifestos:** `https://github.com/igoor1/projetoCI-CD-manifests.git`
* **Imagem Docker:** `https://hub.docker.com/repository/docker/igoor1/your-disc/general`


## Índice

- [Pré-requisitos](#pré-requisitos)
- [Etapa 1: Configurando o Repositório da Aplicação (app-repo)](#etapa-1-configurando-o-repositório-da-aplicação-app-repo)
- [Etapa 2: Configurando o Repositório de Manifestos (manifest-repo)](#etapa-2-configurando-o-repositório-de-manifestos-manifest-repo)
- [Etapa 3: Configurando o ArgoCD](#etapa-3-configurando-o-argocd)
- [Etapa 4: Testando o Fluxo](#etapa-4-testando-o-fluxo)


## Pré-requisitos

- Conta no GitHub.
- Conta no DockerHub.
- Rancher Desktop com Kubernetes habilitado.
- ArgoCD instalado no cluster local.
- Git, Python 3 e Docker instalados localmente.


## Etapa 1: Configurando o Repositório da Aplicação (app-repo)

### 1.1: Estrutura e Dockerfile

1.  Crie um novo repositório no GitHub para sua aplicação.

2. Crie um arquivo `Dockerfile` na raiz para a criação da sua imagem Docker.

**Exemplo de `Dockerfile`:**
 
```dockerfile
FROM python:3.14-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["uvicorn","app.main:app","--host","0.0.0.0"]
```

### 1.2: Configurando os Secrets

Para o GitHub Actions funcionar, ele precisa de permissões. Vá em **Seu Repositório** > **Settings** > **Secrets and variables** > **Actions** e crie os seguintes "Repository secrets":

![gh action secret](https://github.com/user-attachments/assets/8bb589df-a744-4793-b2d7-dc7d974731cb)

- **`DOCKER_USERNAME`**: Seu nome de usuário do Docker Hub.
- **`DOCKER_PASSWORD`**:
    * Vá ao Docker Hub: **Account Settings > Security > New Access Token**.
    * Dê um nome (ex: `github-actions`) e permissões de **Leitura e Escrita (Read & Write)**.
    * Copie o token gerado e cole aqui.
     
![docker hub token](https://github.com/user-attachments/assets/47e64d36-8831-4664-8205-e660154a8be1)

- **`REPOSITORY`**: O nome do seu segundo repositório (o de manifestos).

    - Formato: `seu-usuario/seu-repo-de-manifestos` (ex: `igoor1/projetoCI-CD-manifests`).

- **`TOKEN`**:

    - Vá ao GitHub: **Settings > Developer settings > Personal access tokens > Tokens (classic)**.

    - Clique em **Generate new token (classic)**.

    - Dê um nome e marque o escopo **`repo`** (isso é crucial para permitir o push em outro repositório).

    - Copie o token gerado e cole aqui.

![token gh](https://github.com/user-attachments/assets/4da0761f-26ed-412b-b7e7-636b7fb07b42)

### 1.3: Criando o Workflow (GitHub Actions)

1. No seu **`app-repo`**, crie a pasta `.github/workflows/`.
2. Dentro dela, crie um arquivo (ex: `ci-cd.yml`).
3. Copie e cole o código abaixo.

```yaml
name: CI / CD Pipeline with Argocd

on: 
  push:
    branches: ["main"]
    paths-ignore:
      - 'README.md'
  workflow_dispatch:

jobs:
  CI:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: DockerHub login
        uses: docker/login-action@v3.6.0
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Build and push docker image 
        uses: docker/build-push-action@v6.18.0
        with: 
          context: .
          push: true
          tags: ${{ secrets.DOCKER_USERNAME }}/your-disc:v${{ github.run_number }}
  
  CD:
    needs: [CI]
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout GitOps repo
        uses: actions/checkout@v4
        with:
          repository: ${{ secrets.REPOSITORY }}
          path: projetoci-cd
          token: ${{ secrets.TOKEN }}

      - name: Update manifest
        run: |
          cd projetoci-cd
          sed -i 's|image: ${{ secrets.DOCKER_USERNAME }}/your-disc:.*|image: ${{ secrets.DOCKER_USERNAME }}/your-disc:v${{ github.run_number }}|' k8s/deployment.yaml

      - name: Commit and push manifest changes
        run: |
          cd projetoci-cd
          git config --local user.name 'github-actions[bot]'
          git config --local user.email 'github-actions[bot]@users.noreply.github.com'
          git add k8s/deployment.yaml
          git commit -m "ci: Update image to v${{ github.run_number }}"
          git push origin main
```


## Etapa 2: Configurando o Repositório de Manifestos (manifest-repo)

Este repositório armazena apenas os arquivos YAML do Kubernetes.

1. Crie um novo repositório no GitHub (ex: `projetoCI-CD-manifests`).

2. Crie a estrutura de pastas recomendada:

```
SeuProjeto/
└── k8s
  └── deployment.yaml
  └── service.yaml
```

3. Adicione o conteúdo aos arquivos.

k8s/deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: yourdisc-deployment
  labels:
    app: yourdisc-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: yourdisc-api
  template:
    metadata:
      labels:
        app: yourdisc-api
    spec:
      containers:
      - name: yourdisc-api
        image: igoor1/your-disc:v7
        ports:
        - containerPort: 8000
```

k8s/service.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: yourdisc-service
  labels:
    app: yourdisc-api
spec:
  type: ClusterIP
  selector:
    app: yourdisc-api
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8000
```

4. Faça o commit e push desses arquivos para a branch `main` do seu `manifest-repo`.


## Etapa 3: Configurando o ArgoCD

No seu cluster Local acesse o ArgoCD no seu Navegador: https://localhost:8080

![argocd login](https://github.com/user-attachments/assets/71e13e01-b9d8-4610-8e27-6d77464c7b1e)

1. No ArgoCD, clique em **+ NEW APP**

2. Preencha os campos da seguinte forma: 

- **Application Name:** your-disc-api

- **Project Name:** default

- **Sync Policy:** Automatic (com Prune Resources e Self Heal marcados)

- **Repository URL:** Cole a URL do seu repositório de manifestos.

- **Revision**: HEAD

- **Path:** k8s

- **Cluster URL:** https://kubernetes.default.svc (deve ser o valor padrão para o cluster local)

- **Namespace:** default

Clique em **CREATE**.
![create app](https://github.com/user-attachments/assets/a5564799-37fe-4193-b183-9c1f64b1d4f4)
![create app2](https://github.com/user-attachments/assets/d4160929-4854-42ec-a373-d66bdaf0b76e)

Após o ArgoCD sincronizar a aplicação, todos os pods e services estarão rodando no seu cluster. Para acessar a api, precisamos expor a porta do serviço para a sua máquina local.

![argocd app](https://github.com/user-attachments/assets/fc9e3173-a9fa-42e1-87e5-c13ad4ec25b0)

1. Abra um novo terminal (deixe os outros rodando) e execute o comando port-forward:

```bash
kubectl port-forward svc/yourdisc-service 8081:8080
```

2. Abra seu navegador e acesse a documentação do FastAPI: `http://localhost:8081/docs`.

- Acessando Api pelo navegador:
![api/docs](https://github.com/user-attachments/assets/d9939e0e-627c-4afd-a42b-b59128745d9e)

- Fazendo requisição via Postman.
![postman request](https://github.com/user-attachments/assets/59758d6f-15c4-4121-a71a-601a942b2087)


## Etapa 4: Testando o Fluxo

Agora, vá até o seu app-repo (o da API), faça uma alteração no código (ex: mude um texto em um endpoint) e dê git push para a branch main.

1. **GitHub Actions:** O push irá acionar o workflow.

![gh-actions](https://github.com/user-attachments/assets/dce17792-ab58-4110-953c-5483ff936421)

2. **Job CI:** O job CI irá construir a nova imagem Docker e publicá-la no Docker Hub com uma nova tag (ex: v2, v3, etc.).

3. **Job CD:** O job CD irá fazer o checkout do manifest-repo, alterar a tag da imagem no k8s/deployment.yaml e fazer um novo commit/push.

![pipeline](https://github.com/user-attachments/assets/2030bffe-e9dd-445a-b721-885c7447e34b)

4. **Docker Hub:** A nova imagem aparece atualizada no Docker Hub.

![docker image update](https://github.com/user-attachments/assets/e91b35ca-96e3-4a6d-aaa9-da978ce4712d)

5. **Manifesto:** O repositório de manifestos é atualizado com a nova tag (ex: `v7`).

![manifest update](https://github.com/user-attachments/assets/91448a06-a41c-445b-8ec9-8a0c82ff0312)

6. **ArgoCD:** O ArgoCD detectará a mudança no `manifest-repo` (o novo commit) e aplicará automaticamente as alterações no seu cluster Kubernetes, atualizando os pods para a nova versão da imagem.

![argocd synced](https://github.com/user-attachments/assets/66df88f9-f95f-46ec-872c-459068b2889b)
![kubectl get pods](https://github.com/user-attachments/assets/ae8f610f-1018-499d-a87f-6618b35f4caf)

7. **Aplicação:** A aplicação pode ser acessada pelo navegador já com a alteração aplicada.

![your-disc/docs](https://github.com/user-attachments/assets/0802ffc4-45ea-4630-abe5-92037009a797)

