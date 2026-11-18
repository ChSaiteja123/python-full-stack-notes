(() => {
  "use strict";

  const serviceCatalog = {
    docker: {
      title: "Docker Console",
      category: "CONTAINER PRACTICE",
      description: "Inspect images and containers, then practice a small local lifecycle.",
      prompt: "docker",
      commands: ["docker ps", "docker images", "docker build -t academy-web:dev .", "docker run --name demo-web -p 8080:8000 academy-web:dev", "docker stop demo-web", "docker logs demo-web"],
      guide: "Read-only: docker ps, docker images, docker logs demo-web. Mock changes: build an image, run the sample container, or stop it. A container must have an image before it can run.",
    },
    aws: {
      title: "AWS Practice Console",
      category: "MOCK CLOUD ACCOUNT",
      description: "Explore synthetic identity, EC2, S3, and Auto Scaling data; scaling changes only mock state.",
      prompt: "aws",
      commands: ["aws sts get-caller-identity", "aws ec2 describe-instances", "aws s3 ls", "aws autoscaling describe-auto-scaling-groups", "aws autoscaling set-desired-capacity --auto-scaling-group-name demo-web --desired-capacity 3"],
      guide: "All AWS CLI responses are fictional. Read-only examples inspect mock resources. The set-desired-capacity form accepts 1–4 and changes only the in-memory sandbox after confirmation.",
    },
    grafana: {
      title: "Grafana Explore Console",
      category: "MOCK DASHBOARD AND QUERIES",
      description: "Try a few dashboard and PromQL-style queries against synthetic time-series data.",
      prompt: "grafana",
      commands: ["dashboard list", "dashboard open api-overview", "up", "rate(http_requests_total[5m])", "sum(rate(http_requests_total[5m]))", "alert status"],
      guide: "The query examples return fixed sample series. They do not connect to Grafana or Prometheus. Use the same query ideas in the Prometheus practice console to compare the display and query roles.",
    },
    prometheus: {
      title: "Prometheus Query Console",
      category: "MOCK METRICS",
      description: "Practice selecting targets and reading simple PromQL results from a tiny synthetic dataset.",
      prompt: "prometheus",
      commands: ["targets", "up", "sum by (job) (up)", "rate(http_requests_total[5m])", "rules"],
      guide: "PromQL queries are matched against a fixed sample. A returned value is not a measurement of your machine. Try up, then group it by job, then inspect the example request rate.",
    },
    kubernetes: {
      title: "Kubernetes Practice Console",
      category: "MOCK CLUSTER",
      description: "Inspect pods, deployments, and services, then scale a sample Deployment in mock state.",
      prompt: "kubectl",
      commands: ["kubectl get pods", "kubectl get deployments", "kubectl get services", "kubectl describe pod app-7c9d-a1", "kubectl rollout status deployment/demo-web", "kubectl scale deployment/demo-web --replicas=4"],
      guide: "Read-only: kubectl get and describe. The scale command accepts 1–5 replicas and updates only the mock Deployment; it does not contact a kubeconfig or cluster.",
    },
    terraform: {
      title: "Terraform Practice Console",
      category: "MOCK INFRASTRUCTURE AS CODE",
      description: "Initialize a mock workspace, inspect a plan, and apply it only to the local demonstration state.",
      prompt: "terraform",
      commands: ["terraform init", "terraform plan", "terraform apply", "terraform state list"],
      guide: "The mock plan proposes one sample instance. terraform apply requires the sandbox confirmation and a prior simulated plan. No provider, state file, credentials, or Terraform executable is accessed.",
    },
    ansible: {
      title: "Ansible Practice Console",
      category: "MOCK CONFIGURATION MANAGEMENT",
      description: "Check sample hosts, preview a play, and apply an idempotent configuration to mock state.",
      prompt: "ansible",
      commands: ["ansible all -m ping", "ansible-playbook site.yml --check", "ansible-playbook site.yml"],
      guide: "The check command reports predicted changes. The applying command requires confirmation; the first run converges the mock host and the next run reports no changes.",
    },
    git: {
      title: "Git Practice Console",
      category: "MOCK REPOSITORY",
      description: "Inspect a fictional repository, switch a branch, and practice resolving a staged merge conflict.",
      prompt: "git",
      commands: ["git status --short", "git log --oneline -3", "git switch feature/login", "git merge feature/login", "git add app.py", "git commit -m \"resolve simulated conflict\""],
      guide: "This is not connected to a working tree. Switching and merging update mock history only. The sample merge pauses with a conflict; stage the sample file, then commit the resolution.",
    },
    jenkins: {
      title: "Jenkins Job Console",
      category: "MOCK CI SERVER",
      description: "Inspect example jobs and run a simulated build or approve a sample release gate.",
      prompt: "jenkins",
      commands: ["jobs", "pipeline api-ci", "build api-ci", "approve staging"],
      guide: "These are academy practice-console commands, not Jenkins CLI syntax. Build and approval actions update fictional job state only and require the sandbox confirmation.",
    },
    actions: {
      title: "GitHub Actions Workflow Console",
      category: "MOCK WORKFLOW RUNS",
      description: "Inspect example workflow runs, dispatch a simulated workflow, or rerun a mock failure.",
      prompt: "gh-actions",
      commands: ["workflows", "jobs latest", "run build-and-test", "rerun failed", "approve staging"],
      guide: "These are academy practice-console commands, not the GitHub CLI. Workflow runs and approvals are fictional; no repository, token, or GitHub API is used.",
    },
  };

  const initialState = () => ({
    docker: { imageBuilt: false, containerRunning: false },
    aws: { desiredCapacity: 2 },
    grafana: {},
    prometheus: {},
    kubernetes: { replicas: 3 },
    terraform: { initialized: false, planned: false, applied: false },
    ansible: { converged: false },
    git: { branch: "main", conflict: false, staged: false, merged: false },
    jenkins: { buildNumber: 41, buildStatus: "SUCCESS", stagingApproved: false },
    actions: { runNumber: 87, runStatus: "failure", stagingApproved: false },
  });

  let mockState = initialState();
  let activeService = "docker";
  const terminal = document.querySelector("#terminal-output");
  const commandInput = document.querySelector("#command-input");
  const feedback = document.querySelector("#console-feedback");
  const confirmation = document.querySelector("#confirm-mock-change");

  const appendOutput = (text, kind = "result") => {
    const block = document.createElement("pre");
    block.className = `terminal-line ${kind}`;
    block.textContent = text;
    terminal.append(block);
    while (terminal.children.length > 80) terminal.firstElementChild.remove();
    terminal.scrollTop = terminal.scrollHeight;
  };

  const renderState = () => {
    const state = mockState[activeService];
    const status = document.querySelector("#mock-state");
    const context = document.querySelector("#mock-context");
    const serviceStatus = document.querySelector("#service-status");
    if (activeService === "docker") {
      status.textContent = state.containerRunning ? "demo-web running" : state.imageBuilt ? "Image ready · container stopped" : "No image built";
      context.textContent = "local-sandbox";
    } else if (activeService === "aws") {
      status.textContent = `demo-web desired capacity: ${state.desiredCapacity}`;
      context.textContent = "academy-demo (mock)";
    } else if (activeService === "grafana") {
      status.textContent = "2 dashboards · 1 firing sample alert";
      context.textContent = "sample metrics";
    } else if (activeService === "prometheus") {
      status.textContent = "2 / 3 sample targets up";
      context.textContent = "sample metrics";
    } else if (activeService === "kubernetes") {
      status.textContent = `demo-web · ${state.replicas} desired replicas`;
      context.textContent = "academy-cluster (mock)";
    } else if (activeService === "terraform") {
      status.textContent = state.applied ? "Mock infrastructure applied" : state.planned ? "Plan ready for review" : state.initialized ? "Mock workspace initialized" : "Plan not created";
      context.textContent = "local mock state";
    } else if (activeService === "ansible") {
      status.textContent = state.converged ? "web-01 converged" : "web-01 requires configuration";
      context.textContent = "3 sample hosts";
    } else if (activeService === "git") {
      status.textContent = state.conflict ? "Merge paused · conflict" : state.merged ? "Feature merged" : `On branch ${state.branch}`;
      context.textContent = "academy-demo (mock)";
    } else if (activeService === "jenkins") {
      status.textContent = `#${state.buildNumber} · ${state.buildStatus}${state.stagingApproved ? " · staging approved" : ""}`;
      context.textContent = "mock-ci";
    } else {
      status.textContent = `#${state.runNumber} · ${state.runStatus}${state.stagingApproved ? " · staging approved" : ""}`;
      context.textContent = "sample repository";
    }
    serviceStatus.textContent = "Mock environment ready";
  };

  const renderService = () => {
    const service = serviceCatalog[activeService];
    document.querySelectorAll("[data-service]").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.service === activeService));
    });
    document.querySelector("#console-category").textContent = service.category;
    document.querySelector("#console-title").textContent = service.title;
    document.querySelector("#console-description").textContent = service.description;
    document.querySelector("#terminal-prompt").textContent = `${service.prompt} >`;
    document.querySelector("#command-guide").textContent = service.guide;
    const chips = document.querySelector("#command-chips");
    chips.replaceChildren();
    service.commands.forEach((command) => {
      const chip = document.createElement("button");
      chip.type = "button";
      chip.className = "command-chip";
      chip.textContent = command;
      chip.addEventListener("click", () => {
        commandInput.value = command;
        commandInput.focus();
      });
      chips.append(chip);
    });
    renderState();
  };

  const denied = (reason) => ({ output: `DENIED: ${reason}`, kind: "terminal-denied" });
  const result = (output) => ({ output, kind: "terminal-result" });
  const needsConfirmation = (action) => confirmation.checked
    ? null
    : denied(`Confirm that you want to ${action} in the mock sandbox. No real service is connected.`);

  const dockerCommand = (command, state) => {
    if (command === "docker ps") return result(state.containerRunning
      ? "CONTAINER ID   IMAGE                 STATUS       PORTS\nacademy-demo   academy-web:dev      Up (mock)    0.0.0.0:8080->8000/tcp"
      : "CONTAINER ID   IMAGE   STATUS\n(no running mock containers)");
    if (command === "docker images") return result(state.imageBuilt
      ? "REPOSITORY      TAG   IMAGE ID       CREATED\nacademy-web     dev   sha256:demo01  just now (mock)"
      : "REPOSITORY   TAG   IMAGE ID\n(no mock images yet)");
    if (command === "docker build -t academy-web:dev .") {
      const blocked = needsConfirmation("build an image");
      if (blocked) return blocked;
      state.imageBuilt = true;
      return result("Step 1/3 : FROM python:3.12-slim  [CACHED]\nStep 2/3 : COPY requirements.txt .  [CACHED]\nStep 3/3 : COPY app/ .  [BUILT]\nSuccessfully tagged academy-web:dev (simulation only)");
    }
    if (command === "docker run --name demo-web -p 8080:8000 academy-web:dev") {
      const blocked = needsConfirmation("start the sample container");
      if (blocked) return blocked;
      if (!state.imageBuilt) return denied("Build academy-web:dev first; the mock image does not exist.");
      state.containerRunning = true;
      return result("demo-web started from academy-web:dev (mock).\nPort mapping: 8080 -> 8000. No host port was opened.");
    }
    if (command === "docker stop demo-web") {
      const blocked = needsConfirmation("stop the sample container");
      if (blocked) return blocked;
      if (!state.containerRunning) return denied("demo-web is not running in this mock.");
      state.containerRunning = false;
      return result("demo-web stopped (mock). The image remains available.");
    }
    if (command === "docker logs demo-web") return result(state.containerRunning
      ? "2026-11-17T10:00:00Z INFO  server ready on mock port 8000\n2026-11-17T10:00:01Z INFO  GET /health 200"
      : "No recent mock container output. Start demo-web to create sample logs.");
    return null;
  };

  const awsCommand = (command, state) => {
    if (command === "aws sts get-caller-identity") return result("{\n  \"UserId\": \"MOCK-ACADEMY-USER\",\n  \"Account\": \"000000000000\",\n  \"Arn\": \"arn:aws:iam::000000000000:role/academy-demo\"\n}\nAll identity values are fictional.");
    if (command === "aws ec2 describe-instances") return result("INSTANCE          STATE    PRIVATE IP   SUBNET\n i-demo-web-01     running  10.0.1.24    private-app-a\n i-demo-web-02     running  10.0.2.31    private-app-b");
    if (command === "aws s3 ls") return result("2026-11-17 10:00:00 academy-demo-assets (mock)\n2026-11-17 10:00:00 academy-demo-logs (mock)");
    if (command === "aws autoscaling describe-auto-scaling-groups") return result(`NAME       MIN  DESIRED  MAX  HEALTHY\n demo-web   1    ${state.desiredCapacity}        4    ${state.desiredCapacity} (mock)`);
    const scale = command.match(/^aws autoscaling set-desired-capacity --auto-scaling-group-name demo-web --desired-capacity ([1-4])$/);
    if (scale) {
      const blocked = needsConfirmation("change mock Auto Scaling capacity");
      if (blocked) return blocked;
      state.desiredCapacity = Number(scale[1]);
      return result(`Mock-only update: demo-web desired capacity is now ${state.desiredCapacity}. No AWS API call was made.`);
    }
    return null;
  };

  const metricsCommand = (command, isGrafana) => {
    if (command === "up") return result("job          instance             value\napi          api-01:8000           1\nworker       worker-01:9000        1\ndatabase     db-01:5432            0");
    if (command === "sum by (job) (up)") return result("job          value\napi          1\nworker       1\ndatabase     0");
    if (command === "rate(http_requests_total[5m])") return result("job=\"api\", route=\"/lessons\"   4.20 requests/second\njob=\"api\", route=\"/health\"    0.05 requests/second\nSynthetic sample values; not live measurements.");
    if (command === "sum(rate(http_requests_total[5m]))") return result("{}   4.25 requests/second (synthetic sample)");
    if (isGrafana && command === "dashboard list") return result("api-overview\nservice-health\nAll dashboards are sample fixtures.");
    if (isGrafana && command === "dashboard open api-overview") return result("Dashboard: API Overview\nPanels: request rate · error ratio · p95 latency · target health\nDatasource: academy-prometheus (mock)");
    if (isGrafana && command === "alert status") return result("FIRING   ApiHighErrorRatio   for=4m (mock)\nNORMAL   InstanceDown\nNORMAL   QueueBacklogHigh");
    if (!isGrafana && command === "targets") return result("ENDPOINT           JOB       HEALTH\napi-01:8000        api       UP\nworker-01:9000     worker    UP\ndb-01:5432         database  DOWN (sample)");
    if (!isGrafana && command === "rules") return result("GROUP          NAME                   STATE\nservice-health ApiHighErrorRatio       pending (mock)\nservice-health InstanceDown            inactive (mock)");
    return null;
  };

  const kubernetesCommand = (command, state) => {
    if (command === "kubectl get pods") {
      const rows = Array.from({ length: state.replicas }, (_, index) => `demo-web-${String(index + 1).padStart(2, "0")}   1/1   Running   0   12m`).join("\n");
      return result(`NAME              READY   STATUS    RESTARTS   AGE\n${rows}`);
    }
    if (command === "kubectl get deployments") return result(`NAME       READY              UP-TO-DATE   AVAILABLE\n demo-web   ${state.replicas}/${state.replicas}               ${state.replicas}            ${state.replicas} (mock)`);
    if (command === "kubectl get services") return result("NAME       TYPE        CLUSTER-IP     PORT(S)\n demo-web   ClusterIP   10.96.40.10    80/TCP (mock)");
    if (command === "kubectl describe pod app-7c9d-a1") return result("Name: app-7c9d-a1\nStatus: Running (mock)\nReady: True\nControlled By: ReplicaSet/demo-web\nEvents: Pulled image; started container; readiness probe passed.");
    if (command === "kubectl rollout status deployment/demo-web") return result(`deployment "demo-web" successfully rolled out (${state.replicas} mock replicas ready)`);
    const scale = command.match(/^kubectl scale deployment\/demo-web --replicas=([1-5])$/);
    if (scale) {
      const blocked = needsConfirmation("scale the mock Deployment");
      if (blocked) return blocked;
      state.replicas = Number(scale[1]);
      return result(`deployment.apps/demo-web scaled to ${state.replicas} mock replicas.\nNo kubeconfig or cluster was accessed.`);
    }
    return null;
  };

  const terraformCommand = (command, state) => {
    if (command === "terraform init") {
      const blocked = needsConfirmation("initialize a mock workspace");
      if (blocked) return blocked;
      state.initialized = true;
      return result("Initializing mock backend...\nInitializing provider plugins...\nMock provider: academy/example v0.1.0\nTerraform has been successfully initialized (simulation only).");
    }
    if (command === "terraform plan") {
      if (!state.initialized) return denied("Run the simulated terraform init first.");
      state.planned = true;
      return result(state.applied
        ? "No changes. Mock infrastructure matches the sample configuration."
        : "Terraform will perform the following actions:\n  # academy_instance.web will be created\n  + resource \"academy_instance\" \"web\" { name = \"demo-web\" }\n\nPlan: 1 to add, 0 to change, 0 to destroy. (mock)");
    }
    if (command === "terraform apply") {
      const blocked = needsConfirmation("apply the mock Terraform plan");
      if (blocked) return blocked;
      if (!state.initialized || !state.planned) return denied("Initialize and review a simulated plan before applying.");
      state.applied = true;
      state.planned = false;
      return result("academy_instance.web: Creating... [mock]\nacademy_instance.web: Creation complete [mock]\nApply complete! Resources: 1 added, 0 changed, 0 destroyed. No infrastructure was created.");
    }
    if (command === "terraform state list") return result(state.applied ? "academy_instance.web (mock state only)" : "No managed mock resources. Run init and plan to practice.");
    return null;
  };

  const ansibleCommand = (command, state) => {
    if (command === "ansible all -m ping") return result("web-01 | SUCCESS => {\"ping\": \"pong\"}\nweb-02 | SUCCESS => {\"ping\": \"pong\"}\nweb-03 | SUCCESS => {\"ping\": \"pong\"}\nSample inventory only.");
    if (command === "ansible-playbook site.yml --check") return result(state.converged
      ? "PLAY RECAP\nweb-01 : ok=2 changed=0 unreachable=0 failed=0\nCheck mode predicts no further changes (mock)."
      : "PLAY [Configure web hosts] (check mode)\nTASK [Ensure nginx is installed] changed: [web-01] (predicted)\nTASK [Ensure service is running] changed: [web-01] (predicted)\nPLAY RECAP\nweb-01 : ok=1 changed=1 unreachable=0 failed=0\nNo mock host state was changed.");
    if (command === "ansible-playbook site.yml") {
      const blocked = needsConfirmation("apply the mock Ansible play");
      if (blocked) return blocked;
      const changed = state.converged ? 0 : 1;
      state.converged = true;
      return result(`PLAY [Configure web hosts] (mock apply)\nTASK [Ensure nginx is installed] ${changed ? "changed" : "ok"}: [web-01]\nTASK [Ensure service is running] ok: [web-01]\nPLAY RECAP\nweb-01 : ok=2 changed=${changed} unreachable=0 failed=0\nSecond apply is idempotent in this sample.`);
    }
    return null;
  };

  const gitCommand = (command, state) => {
    if (command === "git status --short") return result(state.conflict
      ? `On branch ${state.branch}\nYou have unmerged paths:\n  both modified: app.py\n${state.staged ? "Resolution staged; commit to finish the mock merge." : "Resolve the conflict, then run git add app.py."}`
      : `On branch ${state.branch}\n${state.merged ? "Merge completed; working tree clean." : "Working tree clean (mock)."}`);
    if (command === "git log --oneline -3") return result(state.merged
      ? "c3d4e5f Merge feature/login (mock)\nb2c3d4e Add feature changes (mock)\na1b2c3d Base commit (mock)"
      : "b2c3d4e Add feature changes (mock)\na1b2c3d Base commit (mock)\n9f8e7d6 Add project scaffold (mock)");
    if (command === "git switch feature/login") {
      const blocked = needsConfirmation("switch the mock branch");
      if (blocked) return blocked;
      state.branch = "feature/login";
      return result("Switched to branch 'feature/login' (mock).");
    }
    if (command === "git merge feature/login") {
      const blocked = needsConfirmation("merge the mock feature branch");
      if (blocked) return blocked;
      if (state.branch !== "main") return denied("Switch to main before simulating the merge.");
      if (state.merged) return result("Already up to date (mock).");
      state.conflict = true;
      return result("Auto-merging app.py\nCONFLICT (content): Merge conflict in app.py\nAutomatic merge failed; resolve the sample conflict, stage it, and commit. (mock)");
    }
    if (command === "git add app.py") {
      const blocked = needsConfirmation("stage the mock conflict resolution");
      if (blocked) return blocked;
      if (!state.conflict) return denied("There is no mock merge conflict to stage.");
      state.staged = true;
      return result("app.py staged for the mock merge commit.");
    }
    if (command === 'git commit -m "resolve simulated conflict"') {
      const blocked = needsConfirmation("commit the mock merge resolution");
      if (blocked) return blocked;
      if (!state.conflict || !state.staged) return denied("Resolve and stage the mock conflict before committing.");
      state.conflict = false;
      state.staged = false;
      state.merged = true;
      return result("[main c3d4e5f] resolve simulated conflict\nMock merge commit created; no repository was changed.");
    }
    return null;
  };

  const jenkinsCommand = (command, state) => {
    if (command === "jobs") return result("NAME              LAST BUILD   STATUS\napi-ci            #41          SUCCESS\ncontainer-build   #18          SUCCESS\nThese are mock jobs.");
    if (command === "pipeline api-ci") return result("api-ci stages (sample):\n1. Checkout\n2. Unit tests\n3. Build image\n4. Security checks\n5. Deploy to staging (approval gate)");
    if (command === "build api-ci") {
      const blocked = needsConfirmation("run the mock Jenkins job");
      if (blocked) return blocked;
      state.buildNumber += 1;
      state.buildStatus = state.buildNumber % 3 === 0 ? "UNSTABLE" : "SUCCESS";
      return result(`Started api-ci #${state.buildNumber} (mock).\nStages: checkout ✓  tests ✓  package ✓\nResult: ${state.buildStatus} (sample run).`);
    }
    if (command === "approve staging") {
      const blocked = needsConfirmation("approve the mock staging gate");
      if (blocked) return blocked;
      state.stagingApproved = true;
      return result("Staging gate approved in mock job state. No deployment occurred.");
    }
    return null;
  };

  const actionsCommand = (command, state) => {
    if (command === "workflows") return result("NAME               FILE                    STATE\nbuild-and-test     ci.yml                  active\nrelease            release.yml             active\nMock repository workflows.");
    if (command === "jobs latest") return result(`Run #${state.runNumber} · build-and-test · ${state.runStatus}\nJobs: lint ${state.runStatus === "success" ? "success" : "success"} · tests ${state.runStatus} · package ${state.runStatus === "success" ? "success" : "skipped"}`);
    if (command === "run build-and-test") {
      const blocked = needsConfirmation("dispatch the mock workflow");
      if (blocked) return blocked;
      state.runNumber += 1;
      state.runStatus = "success";
      return result(`Workflow run #${state.runNumber} queued (mock).\nJobs: lint ✓  tests ✓  package ✓\nAll sample jobs succeeded. No GitHub API call was made.`);
    }
    if (command === "rerun failed") {
      const blocked = needsConfirmation("rerun the mock failed job");
      if (blocked) return blocked;
      if (state.runStatus !== "failure") return denied("There is no failed mock run to rerun.");
      state.runNumber += 1;
      state.runStatus = "success";
      return result(`Rerun #${state.runNumber} completed (mock): tests success; package success.`);
    }
    if (command === "approve staging") {
      const blocked = needsConfirmation("approve the mock deployment environment");
      if (blocked) return blocked;
      state.stagingApproved = true;
      return result("Environment approval recorded in mock workflow state. No deployment occurred.");
    }
    return null;
  };

  const handlers = {
    docker: dockerCommand,
    aws: awsCommand,
    grafana: (command) => metricsCommand(command, true),
    prometheus: (command) => metricsCommand(command, false),
    kubernetes: kubernetesCommand,
    terraform: terraformCommand,
    ansible: ansibleCommand,
    git: gitCommand,
    jenkins: jenkinsCommand,
    actions: actionsCommand,
  };

  const runCommand = (rawCommand) => {
    const command = rawCommand.trim().replace(/\s+/g, " ");
    if (!command) return;
    appendOutput(`${serviceCatalog[activeService].prompt} > ${command}`, "terminal-command");
    if (command.length > 240 || /[;&|<>`]/.test(command) || command.includes("$(")) {
      appendOutput("Refused: only a single supported practice command or query is accepted. Nothing was executed.", "terminal-denied");
      feedback.textContent = "Unsupported input was refused. Use a command chip or the allowlisted examples.";
      return;
    }
    if (command === "help") {
      appendOutput(serviceCatalog[activeService].commands.join("\n"), "terminal-result");
      return;
    }
    if (command === "clear") {
      terminal.replaceChildren();
      return;
    }
    const response = handlers[activeService](command, mockState[activeService]);
    if (!response) {
      appendOutput("Unsupported practice command. Use a command chip or `help`. Nothing was executed.", "terminal-denied");
      feedback.textContent = "Command not in this console's supported practice set.";
      return;
    }
    appendOutput(response.output, response.kind);
    feedback.textContent = response.kind === "terminal-denied"
      ? "The simulation blocked that action or prerequisite."
      : "Simulation response added above; no external service was called.";
    renderState();
  };

  document.querySelectorAll("[data-service]").forEach((button) => {
    button.addEventListener("click", () => {
      activeService = button.dataset.service;
      renderService();
      commandInput.value = "";
      feedback.textContent = "Read-only examples can be run immediately. Simulated changes require the confirmation above.";
    });
  });

  document.querySelector("#command-form").addEventListener("submit", (event) => {
    event.preventDefault();
    runCommand(commandInput.value);
    commandInput.value = "";
    commandInput.focus();
  });

  document.querySelector("#clear-terminal").addEventListener("click", () => {
    terminal.replaceChildren();
    feedback.textContent = "Output cleared. Mock service state was not reset.";
  });

  document.querySelector("#reset-console").addEventListener("click", () => {
    mockState = initialState();
    confirmation.checked = false;
    terminal.replaceChildren();
    appendOutput("All mock service state was reset for this page session. No real system was changed.", "terminal-system");
    renderService();
    feedback.textContent = "Mock state reset. Confirm again before practicing simulated changes.";
  });

  renderService();
})();
