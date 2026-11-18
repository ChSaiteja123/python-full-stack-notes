(() => {
  "use strict";

  document.querySelectorAll("[data-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      const filter = button.dataset.filter;
      document.querySelectorAll("[data-filter]").forEach((item) => {
        item.setAttribute("aria-pressed", String(item === button));
      });
      document.querySelectorAll(".deep-lab[data-lab]").forEach((lab) => {
        const matches = filter === "all"
          || lab.dataset.lab === filter
          || (lab.dataset.lab === "devops" && (filter === "devops" || lab.dataset.topic === filter));
        lab.hidden = !matches;
      });
    });
  });

  const dockerLab = document.querySelector("#docker-lab");
  if (dockerLab) {
    const changeInput = dockerLab.querySelector("#docker-change");
    const status = dockerLab.querySelector("[data-docker-status]");
    const layers = Array.from(dockerLab.querySelectorAll("[data-docker-layer]"));
    const imageStatus = dockerLab.querySelector("#docker-image");
    const containerStatus = dockerLab.querySelector("#docker-container");
    const cachedStatus = dockerLab.querySelector("#docker-cached");
    const runButton = dockerLab.querySelector('[data-docker-action="run"]');
    let built = false;
    let running = false;

    dockerLab.querySelector('[data-docker-action="build"]').addEventListener("click", () => {
      const invalidatedFrom = { base: 0, dependencies: 2, source: 3, none: layers.length }[changeInput.value];
      layers.forEach((layer, index) => {
        const rebuild = index >= invalidatedFrom;
        layer.classList.toggle("is-rebuild", rebuild);
        layer.classList.toggle("is-cached", !rebuild);
        layer.querySelector("em").textContent = rebuild ? "REBUILD · changed input" : "CACHED · unchanged";
      });
      const cached = invalidatedFrom;
      cachedStatus.textContent = `${cached} / ${layers.length}`;
      built = true;
      imageStatus.textContent = "academy-web:dev (mock image)";
      containerStatus.textContent = running ? "Existing container still running" : "Not created";
      runButton.disabled = false;
      status.classList.remove("error");
      status.textContent = invalidatedFrom === layers.length
        ? `No input changed; all ${layers.length} layers were reused in this build simulation.`
        : `Build simulation complete. ${cached} layer(s) reused; ${layers.length - cached} rebuilt.`;
    });
    runButton.addEventListener("click", () => {
      if (!built) {
        status.classList.add("error");
        status.textContent = "Build the mock image before creating a container.";
        return;
      }
      running = true;
      containerStatus.textContent = "Running from academy-web:dev (simulation)";
      status.classList.remove("error");
      status.textContent = "A sample container is running in this page's mock state. No Docker daemon or port was used.";
    });
    dockerLab.querySelector('[data-docker-action="reset"]').addEventListener("click", () => {
      built = false;
      running = false;
      cachedStatus.textContent = "—";
      imageStatus.textContent = "Not built";
      containerStatus.textContent = "Not created";
      runButton.disabled = true;
      layers.forEach((layer, index) => {
        layer.classList.remove("is-rebuild", "is-cached");
        layer.querySelector("em").textContent = ["Base image", "System dependencies", "Dependency layer", "Application layer", "Image configuration"][index];
      });
      status.classList.remove("error");
      status.textContent = "Reset. Choose a change and simulate the build.";
    });
  }

  const awsLab = document.querySelector("#aws-lab");
  if (awsLab) {
    const scenarioInput = awsLab.querySelector("#aws-scenario");
    const status = awsLab.querySelector("[data-aws-status]");
    const nextButton = awsLab.querySelector('[data-aws-action="next"]');
    const nodes = Array.from(awsLab.querySelectorAll("[data-aws-node]"));
    const result = awsLab.querySelector("#aws-result");
    const explanation = awsLab.querySelector("#aws-explanation");
    const stages = ["dns", "alb", "app", "db", "response"];
    let scenario = "healthy";
    let active = -1;
    let finished = false;

    const paint = (blocked = null) => {
      nodes.forEach((node) => {
        const index = stages.indexOf(node.dataset.awsNode);
        node.classList.toggle("is-complete", index >= 0 && index < active && index < blocked);
        node.classList.toggle("is-active", index === active && index !== blocked);
        node.classList.toggle("is-blocked", index === blocked);
      });
      nextButton.disabled = active < 0 || finished;
    };
    const stopAt = (stage, code, message) => {
      active = stages.indexOf(stage);
      finished = true;
      result.textContent = code;
      explanation.textContent = message;
      status.textContent = `Trace stopped at ${stage.toUpperCase()}. No later hop was attempted.`;
      paint(active);
    };
    awsLab.querySelector('[data-aws-action="start"]').addEventListener("click", () => {
      scenario = scenarioInput.value;
      active = 0;
      finished = false;
      result.textContent = "—";
      explanation.textContent = "The request is entering the sample architecture.";
      status.textContent = "At DNS: resolve the application hostname.";
      status.classList.remove("error");
      paint();
    });
    nextButton.addEventListener("click", () => {
      if (active < 0 || finished) return;
      if (active === 1 && scenario === "no-targets") {
        stopAt("alb", "503 · No healthy targets", "The load balancer has no healthy application target to receive the request.");
        return;
      }
      if (active === 3 && scenario === "db-unreachable") {
        stopAt("db", "5xx · Dependency unavailable", "The application could not reach its database. Check routes, security-group sources, subnet placement, and database health.");
        return;
      }
      if (active === stages.length - 1) {
        finished = true;
        result.textContent = scenario === "db-public" ? "200 · Sample response; network risk" : "200 · Sample response";
        explanation.textContent = scenario === "db-public"
          ? "The sample request succeeded, but the database's public route is an exposure risk. Restrict its network path; successful reachability is not proof of safe design."
          : "DNS, load-balancer routing, healthy application targets, and the private database path all succeeded in the mock.";
        status.textContent = scenario === "db-public"
          ? "Trace completed with a warning: a publicly routed database should be reviewed and restricted."
          : "Trace complete: the sample response reached the client.";
        paint();
        return;
      }
      active += 1;
      const name = nodes[active].querySelector("strong").textContent;
      status.textContent = `At ${name}: inspect this hop before continuing.`;
      paint();
    });
    awsLab.querySelector('[data-aws-action="reset"]').addEventListener("click", () => {
      active = -1;
      finished = false;
      result.textContent = "—";
      explanation.textContent = "No cloud request simulated.";
      status.textContent = "Choose a scenario and start at DNS.";
      status.classList.remove("error");
      nodes.forEach((node) => node.classList.remove("is-active", "is-complete", "is-blocked"));
      nextButton.disabled = true;
    });
  }

  const terraformLab = document.querySelector("#terraform-lab");
  if (terraformLab) {
    const driftInput = terraformLab.querySelector("#terraform-drift");
    const table = terraformLab.querySelector("#terraform-plan");
    const status = terraformLab.querySelector("[data-terraform-status]");
    const review = terraformLab.querySelector("#terraform-review");
    const applyButton = terraformLab.querySelector('[data-terraform-action="apply"]');
    let planReady = false;
    let applied = false;
    let plannedScenario = "aligned";

    const writePlan = (scenario) => {
      const resources = [
        { name: "academy_instance.web", desired: "2 mock instances", action: scenario === "web-missing" ? "+ create" : "no-op" },
        { name: "academy_database.main", desired: "size: small", action: scenario === "db-drift" ? "~ update in-place" : "no-op" },
        { name: "academy_security_group.app", desired: "app-only ingress", action: "no-op" },
      ];
      if (scenario === "extra-resource") {
        resources.push({ name: "academy_instance.debug", desired: "absent", action: "- destroy" });
      }
      if (applied) resources.forEach((resource) => { resource.action = "no-op"; });
      table.replaceChildren();
      resources.forEach((resource) => {
        const row = table.insertRow();
        row.insertCell().textContent = resource.name;
        row.insertCell().textContent = resource.desired;
        const action = row.insertCell();
        action.textContent = resource.action;
        action.className = resource.action === "no-op" ? "plan-noop" : resource.action.startsWith("-") ? "plan-destroy" : "plan-change";
      });
      return resources;
    };

    terraformLab.querySelector('[data-terraform-action="plan"]').addEventListener("click", () => {
      plannedScenario = driftInput.value;
      const resources = writePlan(plannedScenario);
      planReady = true;
      applied = false;
      review.disabled = false;
      review.checked = false;
      applyButton.disabled = true;
      const creates = resources.filter((resource) => resource.action.startsWith("+")).length;
      const updates = resources.filter((resource) => resource.action.startsWith("~")).length;
      const destroys = resources.filter((resource) => resource.action.startsWith("-")).length;
      status.textContent = `Plan ready: ${creates} to add, ${updates} to change, ${destroys} to destroy. Review each row before simulating apply.`;
      status.classList.remove("error");
    });
    review.addEventListener("change", () => {
      applyButton.disabled = !planReady || !review.checked || applied;
    });
    applyButton.addEventListener("click", () => {
      if (!planReady || !review.checked || applied) return;
      applied = true;
      planReady = false;
      writePlan(plannedScenario);
      review.disabled = true;
      applyButton.disabled = true;
      status.textContent = "Mock plan applied. Re-create the plan to see that sample state now matches the declared configuration.";
    });
    terraformLab.querySelector('[data-terraform-action="reset"]').addEventListener("click", () => {
      planReady = false;
      applied = false;
      plannedScenario = "aligned";
      review.checked = false;
      review.disabled = true;
      applyButton.disabled = true;
      table.replaceChildren();
      const row = table.insertRow();
      const cell = row.insertCell();
      cell.colSpan = 3;
      cell.textContent = "Create a plan to inspect proposed actions.";
      status.textContent = "No plan created.";
      status.classList.remove("error");
    });
  }

  const ansibleLab = document.querySelector("#ansible-lab");
  if (ansibleLab) {
    const scenarioInput = ansibleLab.querySelector("#ansible-scenario");
    const checkMode = ansibleLab.querySelector("#ansible-check");
    const status = ansibleLab.querySelector("[data-ansible-status]");
    const hosts = Array.from(ansibleLab.querySelectorAll("[data-host]"));
    const counters = {
      ok: ansibleLab.querySelector("#ansible-ok"),
      changed: ansibleLab.querySelector("#ansible-changed"),
      unreachable: ansibleLab.querySelector("#ansible-unreachable"),
      run: ansibleLab.querySelector("#ansible-run"),
    };
    let converged = false;
    let runNumber = 0;

    ansibleLab.querySelector('[data-ansible-action="run"]').addEventListener("click", () => {
      const scenario = scenarioInput.value;
      const results = hosts.map((host, index) => {
        if (scenario === "unreachable" && index === 2) return { text: "UNREACHABLE · no connection", type: "unreachable" };
        if (scenario === "drift" && index === 1 && !converged) {
          if (!checkMode.checked) converged = true;
          return { text: checkMode.checked ? "CHANGED · predicted only" : "CHANGED · configured", type: "changed" };
        }
        return { text: "OK · desired state present", type: "ok" };
      });
      runNumber += 1;
      let ok = 0;
      let changed = 0;
      let unreachable = 0;
      results.forEach((result, index) => {
        const host = hosts[index];
        host.querySelector("span").textContent = result.text;
        host.classList.remove("host-ok", "host-changed", "host-unreachable");
        host.classList.add(`host-${result.type}`);
        if (result.type === "ok") ok += 1;
        else if (result.type === "changed") changed += 1;
        else unreachable += 1;
      });
      counters.ok.textContent = String(ok);
      counters.changed.textContent = String(changed);
      counters.unreachable.textContent = String(unreachable);
      counters.run.textContent = String(runNumber);
      status.textContent = `Run ${runNumber}: ${ok} ok, ${changed} changed${checkMode.checked ? " (predicted)" : ""}, ${unreachable} unreachable. ${checkMode.checked ? "Check mode made no host changes." : "Applying tasks converge configured mock hosts."}`;
      status.classList.remove("error");
    });
    ansibleLab.querySelector('[data-ansible-action="reset"]').addEventListener("click", () => {
      converged = false;
      runNumber = 0;
      counters.ok.textContent = "—";
      counters.changed.textContent = "—";
      counters.unreachable.textContent = "—";
      counters.run.textContent = "0";
      hosts.forEach((host) => {
        host.querySelector("span").textContent = "Not evaluated";
        host.classList.remove("host-ok", "host-changed", "host-unreachable");
      });
      status.textContent = "Choose a host condition and run the play.";
      status.classList.remove("error");
    });
  }

  const gitLab = document.querySelector("#git-lab");
  if (gitLab) {
    const scenarioInput = gitLab.querySelector("#git-scenario");
    const status = gitLab.querySelector("[data-git-status]");
    const result = gitLab.querySelector("[data-git-result]");
    const conflict = gitLab.querySelector("[data-git-conflict]");
    const resolution = gitLab.querySelector("[data-git-resolution]");
    const nodes = Array.from(gitLab.querySelectorAll("[data-git-node]"));
    let pendingConflict = false;

    const clearGraph = () => {
      nodes.forEach((node) => node.classList.remove("commit-active", "commit-complete", "commit-merge"));
      nodes.find((node) => node.dataset.gitNode === "main-tip").hidden = false;
      nodes.find((node) => node.dataset.gitNode === "merge-tip").hidden = true;
      nodes.find((node) => node.dataset.gitNode === "feature-tip").hidden = false;
    };
    gitLab.querySelector('[data-git-action="merge"]').addEventListener("click", () => {
      const scenario = scenarioInput.value;
      clearGraph();
      pendingConflict = scenario === "conflict";
      conflict.hidden = !pendingConflict;
      resolution.hidden = !pendingConflict;
      nodes.find((node) => node.dataset.gitNode === "main-base").classList.add("commit-complete");
      nodes.find((node) => node.dataset.gitNode === "feature-base").classList.add("commit-complete");
      nodes.find((node) => node.dataset.gitNode === "feature-tip").classList.add("commit-active");
      if (scenario === "fast-forward") {
        nodes.find((node) => node.dataset.gitNode === "main-tip").hidden = true;
        result.textContent = "Fast-forward: main moves to the feature tip. No merge commit is needed because main had not diverged.";
        status.textContent = "Integration complete: branch pointer advanced.";
      } else {
        nodes.find((node) => node.dataset.gitNode === "main-tip").classList.add("commit-active");
        if (pendingConflict) {
          result.textContent = "Merge paused: both branches changed the same line. Choose the intended value, then mark the sample conflict resolved.";
          status.textContent = "Conflict requires an explicit resolution; Git cannot infer intent.";
        } else {
          nodes.find((node) => node.dataset.gitNode === "merge-tip").hidden = false;
          nodes.find((node) => node.dataset.gitNode === "merge-tip").classList.add("commit-merge");
          result.textContent = "Merge commit M joins the main and feature histories. The changes did not overlap.";
          status.textContent = "Clean merge simulated.";
        }
      }
      status.classList.remove("error");
    });
    gitLab.querySelector('[data-git-action="resolve"]').addEventListener("click", () => {
      if (!pendingConflict) return;
      const value = scenarioInput.value === "conflict" && gitLab.querySelector("#git-resolution").value === "main" ? "20" : "45";
      nodes.find((node) => node.dataset.gitNode === "merge-tip").hidden = false;
      nodes.find((node) => node.dataset.gitNode === "merge-tip").classList.add("commit-merge");
      pendingConflict = false;
      conflict.hidden = true;
      resolution.hidden = true;
      result.textContent = `Conflict resolved with timeout = ${value}; merge commit M joins the two branch histories (mock).`;
      status.textContent = "Resolution recorded in the sample graph. No repository was modified.";
    });
    gitLab.querySelector('[data-git-action="reset"]').addEventListener("click", () => {
      pendingConflict = false;
      clearGraph();
      conflict.hidden = true;
      resolution.hidden = true;
      result.textContent = "No merge simulated.";
      status.textContent = "Choose a branch history and simulate integration.";
      status.classList.remove("error");
    });
    clearGraph();
  }

  const kubernetesLab = document.querySelector("#kubernetes-lab");
  if (kubernetesLab) {
    const scenarioInput = kubernetesLab.querySelector("#k8s-scenario");
    const status = kubernetesLab.querySelector("[data-k8s-status]");
    const podGrid = kubernetesLab.querySelector("#k8s-pods");
    const podNames = ["app-7c9d-a1", "app-7c9d-b2", "app-7c9d-c3"];
    const readyCount = kubernetesLab.querySelector("#k8s-ready");
    const endpointCount = kubernetesLab.querySelector("#k8s-endpoints");
    const rollout = kubernetesLab.querySelector("#k8s-rollout");
    const nodes = Array.from(kubernetesLab.querySelectorAll(".k8s-flow .diagram-node"));
    const reconcile = () => {
      const scenario = scenarioInput.value;
      const podStatus = {
        ready: ["Running · Ready", "Running · Ready", "Running · Ready"],
        "image-pull": ["ImagePullBackOff", "ImagePullBackOff", "ImagePullBackOff"],
        readiness: ["Running · NotReady", "Running · NotReady", "Running · NotReady"],
        liveness: ["CrashLoopBackOff · restarting", "CrashLoopBackOff · restarting", "CrashLoopBackOff · restarting"],
      }[scenario];
      const ready = scenario === "ready" ? 3 : 0;
      Array.from(podGrid.children).forEach((card, index) => {
        card.querySelector("span").textContent = podStatus[index];
        card.classList.remove("pod-ready", "pod-pending", "pod-failed");
        card.classList.add(ready ? "pod-ready" : scenario === "readiness" ? "pod-pending" : "pod-failed");
      });
      readyCount.textContent = `${ready} / 3`;
      endpointCount.textContent = String(ready);
      rollout.textContent = scenario === "ready" ? "Complete" : scenario === "image-pull" ? "Stalled · image pull" : scenario === "readiness" ? "Progressing · not ready" : "Stalled · restarting";
      nodes[0].classList.add("is-complete");
      nodes[1].classList.add("is-complete");
      nodes[2].classList.add(ready ? "is-complete" : "is-blocked");
      nodes[3].classList.toggle("is-complete", ready > 0);
      status.textContent = ready
        ? "Reconcile complete: 3 desired pods are Ready and selected as Service endpoints."
        : scenario === "image-pull"
          ? "Controller maintains the desired count, but image pulls fail. No pod is Ready; the Service has no ready endpoint."
          : scenario === "readiness"
            ? "Containers run, but readiness fails. Pods remain out of Service endpoints until they become Ready."
            : "Repeated liveness failures restart containers; pods can enter back-off and are not Ready endpoints.";
    };
    kubernetesLab.querySelector('[data-k8s-action="reconcile"]').addEventListener("click", reconcile);
    kubernetesLab.querySelector('[data-k8s-action="reset"]').addEventListener("click", () => {
      Array.from(podGrid.children).forEach((card, index) => {
        card.querySelector("strong").textContent = podNames[index];
        card.querySelector("span").textContent = "Not created";
        card.classList.remove("pod-ready", "pod-pending", "pod-failed");
      });
      readyCount.textContent = "0 / 3";
      endpointCount.textContent = "0";
      rollout.textContent = "Not started";
      nodes.forEach((node) => node.classList.remove("is-complete", "is-blocked", "is-active"));
      nodes[0].classList.add("is-complete");
      nodes[1].classList.add("is-complete");
      status.textContent = "Desired replicas: 3 · No reconciliation run.";
    });
  }

  const params = new URLSearchParams(window.location.search);
  const requestedLab = params.get("lab");
  if (requestedLab) {
    document.querySelectorAll(".deep-lab[data-lab]").forEach((lab) => {
      const matches = lab.dataset.lab === requestedLab
        || (lab.dataset.lab === "devops" && (requestedLab === "devops" || lab.dataset.topic === requestedLab));
      lab.hidden = !matches;
    });
    document.querySelectorAll("[data-filter]").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.filter === requestedLab));
    });
  }
})();
