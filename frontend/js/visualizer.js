(() => {
  "use strict";

  document.querySelectorAll("[data-stepper]").forEach((stepper) => {
    const steps = Array.from(stepper.querySelectorAll("[data-step]"));
    const status = stepper.querySelector(".step-status");
    const buttons = Array.from(stepper.querySelectorAll("[data-action]"));
    const playButton = buttons.find((button) => button.dataset.action === "play");
    if (!steps.length || !status) return;

    let active = 0;
    let timer = null;
    const render = () => {
      steps.forEach((step, index) => {
        if (index === active) step.setAttribute("aria-current", "step");
        else step.removeAttribute("aria-current");
      });
      status.textContent = `Step ${active + 1} of ${steps.length}: ${steps[active].textContent}`;
      const previous = buttons.find((button) => button.dataset.action === "previous");
      const next = buttons.find((button) => button.dataset.action === "next");
      if (previous) previous.disabled = active === 0;
      if (next) next.disabled = active === steps.length - 1;
    };
    const stop = () => {
      if (timer !== null) {
        window.clearInterval(timer);
        timer = null;
      }
      if (playButton) playButton.textContent = "Play";
    };
    const next = () => {
      if (active >= steps.length - 1) {
        stop();
        return;
      }
      active += 1;
      render();
      if (active === steps.length - 1) stop();
    };

    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        const action = button.dataset.action;
        if (action === "next") {
          stop();
          next();
        } else if (action === "previous") {
          stop();
          active = Math.max(0, active - 1);
          render();
        } else if (action === "reset") {
          stop();
          active = 0;
          render();
        } else if (action === "play") {
          if (timer === null && active < steps.length - 1) {
            timer = window.setInterval(next, 1800);
            button.textContent = "Pause";
          } else {
            stop();
          }
        }
      });
    });
    document.addEventListener("visibilitychange", () => {
      if (document.hidden) stop();
    });
    render();
  });

  document.querySelectorAll("[data-filter]").forEach((button) => {
    button.addEventListener("click", () => {
      const filter = button.dataset.filter;
      document.querySelectorAll("[data-filter]").forEach((item) => {
        item.setAttribute("aria-pressed", String(item === button));
      });
      document.querySelectorAll("[data-lab]").forEach((lab) => {
        lab.hidden = filter !== "all" && lab.dataset.lab !== filter;
      });
    });
  });

  const loopLab = document.querySelector("#python-state-lab");
  if (loopLab) {
    const valuesInput = loopLab.querySelector("#loop-values");
    const operationInput = loopLab.querySelector("#loop-operation");
    const status = loopLab.querySelector("[data-loop-status]");
    const trace = loopLab.querySelector("#loop-trace");
    const nextButton = loopLab.querySelector('[data-loop-action="next"]');
    const nodes = Array.from(loopLab.querySelectorAll("[data-loop-node]"));
    const output = {
      index: loopLab.querySelector("#loop-index"),
      current: loopLab.querySelector("#loop-current"),
      accumulator: loopLab.querySelector("#loop-accumulator"),
      result: loopLab.querySelector("#loop-result"),
    };
    let values = [];
    let currentIndex = 0;
    let accumulator = 0;
    let loaded = false;

    const setNode = (name) => {
      const order = ["input", "read", "update", "output"];
      const activeIndex = order.indexOf(name);
      nodes.forEach((node) => {
        const index = order.indexOf(node.dataset.loopNode);
        node.classList.toggle("is-active", index === activeIndex);
        node.classList.toggle("is-complete", loaded && index < activeIndex);
      });
    };
    const clearTrace = () => {
      trace.replaceChildren();
      const row = trace.insertRow();
      const cell = row.insertCell();
      cell.colSpan = 3;
      cell.textContent = "Load a valid input to create a trace.";
    };
    const start = () => {
      const rawValues = valuesInput.value.split(",").map((part) => part.trim());
      const parsed = rawValues.map((part) => part === "" ? Number.NaN : Number(part));
      if (parsed.length < 1 || parsed.length > 12 || parsed.some((value) => !Number.isFinite(value) || Math.abs(value) > 1e9)) {
        loaded = false;
        currentIndex = 0;
        nextButton.disabled = true;
        status.textContent = "Enter 1–12 comma-separated numbers with magnitude at most 1,000,000,000. Empty items, non-numeric values, and larger numbers are not accepted.";
        status.classList.add("error");
        clearTrace();
        nodes.forEach((node) => node.classList.remove("is-active", "is-complete"));
        return;
      }
      values = parsed;
      currentIndex = 0;
      accumulator = operationInput.value === "maximum" ? Number.NEGATIVE_INFINITY : 0;
      loaded = true;
      nextButton.disabled = false;
      status.classList.remove("error");
      status.textContent = `${values.length} values loaded. Predict the result, then process the first value.`;
      output.index.textContent = "0";
      output.current.textContent = "—";
      output.accumulator.textContent = operationInput.value === "maximum" ? "—" : "0";
      output.result.textContent = "—";
      trace.replaceChildren();
      setNode("input");
    };
    const step = () => {
      if (!loaded || currentIndex >= values.length) return;
      const value = values[currentIndex];
      accumulator = operationInput.value === "maximum" ? Math.max(accumulator, value) : accumulator + value;
      currentIndex += 1;
      output.index.textContent = String(currentIndex);
      output.current.textContent = String(value);
      output.accumulator.textContent = String(Number(accumulator.toFixed(6)));
      const row = trace.insertRow();
      row.insertCell().textContent = String(currentIndex);
      row.insertCell().textContent = String(value);
      row.insertCell().textContent = String(Number(accumulator.toFixed(6)));
      setNode("update");
      if (currentIndex === values.length) {
        const result = operationInput.value === "average" ? accumulator / values.length : accumulator;
        output.result.textContent = String(Number(result.toFixed(6)));
        nextButton.disabled = true;
        status.textContent = `Done: ${operationInput.value} of ${values.length} values is ${output.result.textContent}. The loop exhausted its input.`;
        setNode("output");
      } else {
        status.textContent = `Iteration ${currentIndex} read ${value}; state is now ${output.accumulator.textContent}. Process the next value when ready.`;
      }
    };

    loopLab.querySelector('[data-loop-action="start"]').addEventListener("click", start);
    nextButton.addEventListener("click", step);
    loopLab.querySelector('[data-loop-action="reset"]').addEventListener("click", () => {
      loaded = false;
      currentIndex = 0;
      nextButton.disabled = true;
      status.classList.remove("error");
      status.textContent = "Reset. Load the input to begin again.";
      output.index.textContent = "—";
      output.current.textContent = "—";
      output.accumulator.textContent = "—";
      output.result.textContent = "—";
      clearTrace();
      nodes.forEach((node) => node.classList.remove("is-active", "is-complete"));
    });
  }

  const requestLab = document.querySelector("#request-pipeline-lab");
  if (requestLab) {
    const scenarioInput = requestLab.querySelector("#request-scenario");
    const status = requestLab.querySelector("[data-request-status]");
    const nextButton = requestLab.querySelector('[data-request-action="next"]');
    const nodes = Array.from(requestLab.querySelectorAll("[data-request-node]"));
    const code = requestLab.querySelector("#request-code");
    const explanation = requestLab.querySelector("#request-explanation");
    const routes = {
      success: {
        result: "200 · OK",
        message: "Identity is known, object ownership and input checks pass, and the scoped record is returned.",
        stop: null,
      },
      anonymous: {
        result: "401 · Authentication required",
        message: "The request stops at the session/authentication boundary. No record lookup occurs.",
        stop: "route",
      },
      forbidden: {
        result: "403 · Forbidden",
        message: "The user is authenticated but does not own this record. Authorization blocks the lookup or mutation.",
        stop: "view",
      },
      invalid: {
        result: "400 · Invalid input",
        message: "The request reaches validation but fails the input contract; the database is not changed.",
        stop: "view",
      },
      missing: {
        result: "404 · Not found",
        message: "The scoped lookup found no accessible record. Applications may use a uniform response to avoid leaking record existence.",
        stop: "data",
      },
    };
    const order = ["browser", "route", "view", "data", "response"];
    let route = routes.success;
    let active = -1;
    const render = () => {
      nodes.forEach((node) => {
        const index = order.indexOf(node.dataset.requestNode);
        const blockedAt = route.stop ? order.indexOf(route.stop) : order.length;
        node.classList.toggle("is-complete", index >= 0 && index < active && index < blockedAt);
        node.classList.toggle("is-active", index === active && (!route.stop || active < blockedAt));
        node.classList.toggle("is-blocked", Boolean(route.stop) && index === blockedAt && active >= blockedAt);
      });
      if (route.stop && active >= order.indexOf(route.stop)) {
        code.textContent = route.result;
        explanation.textContent = route.message;
        status.textContent = `Request stopped at ${route.stop}; subsequent data and side-effect stages were not run.`;
        nextButton.disabled = true;
      } else if (active >= order.length) {
        code.textContent = route.result;
        explanation.textContent = route.message;
        status.textContent = `Trace complete: ${route.message}`;
        nextButton.disabled = true;
      } else {
        const name = nodes.find((node) => node.dataset.requestNode === order[active])?.querySelector("strong")?.textContent || "request";
        code.textContent = "—";
        explanation.textContent = "No response has been produced yet.";
        status.textContent = `At boundary ${active + 1} of ${order.length}: ${name}.`;
        nextButton.disabled = false;
      }
    };
    const start = () => {
      route = routes[scenarioInput.value] || routes.success;
      active = 0;
      status.classList.remove("error");
      status.textContent = "Request entered the application.";
      code.textContent = "—";
      explanation.textContent = "No response has been produced yet.";
      render();
    };
    requestLab.querySelector('[data-request-action="start"]').addEventListener("click", start);
    nextButton.addEventListener("click", () => {
      if (active >= order.length) return;
      active += 1;
      render();
    });
    requestLab.querySelector('[data-request-action="reset"]').addEventListener("click", () => {
      active = -1;
      code.textContent = "—";
      explanation.textContent = "No request has been simulated.";
      nextButton.disabled = true;
      status.textContent = "Reset. Choose a scenario, then start the request.";
      nodes.forEach((node) => node.classList.remove("is-active", "is-complete", "is-blocked"));
    });
  }

  const ragLab = document.querySelector("#rag-retrieval-lab");
  if (ragLab) {
    const documents = [
      { id: "python-loop", title: "Python loops and accumulators", text: "A loop processes each value and updates a running accumulator.", scope: "public", words: ["loop", "python", "value", "accumulator"] },
      { id: "docker-images", title: "Container images and deployment", text: "Container images package application layers for repeatable deployment.", scope: "public", words: ["container", "image", "deployment", "docker"] },
      { id: "django-auth", title: "Django authentication and permissions", text: "Authentication identifies a user; object permissions decide access.", scope: "public", words: ["django", "authentication", "permission", "user", "access"] },
      { id: "billing-private", title: "Internal account billing runbook", text: "Private account billing procedures and finance escalation contacts.", scope: "staff", words: ["account", "billing", "finance", "private"] },
      { id: "rag-citations", title: "Grounded answers and citations", text: "Retrieve scoped passages and cite the source used for each claim.", scope: "public", words: ["retrieval", "source", "citation", "grounded", "answer"] },
    ];
    const queryInput = ragLab.querySelector("#rag-query");
    const roleInput = ragLab.querySelector("#rag-role");
    const topKInput = ragLab.querySelector("#rag-top-k");
    const topKValue = ragLab.querySelector("#rag-top-k-value");
    const status = ragLab.querySelector("[data-rag-status]");
    const results = ragLab.querySelector("#rag-results");
    topKInput.addEventListener("input", () => {
      topKValue.value = topKInput.value;
      topKValue.textContent = topKInput.value;
    });
    ragLab.querySelector('[data-rag-action="retrieve"]').addEventListener("click", () => {
      const terms = queryInput.value.toLowerCase().match(/[a-z0-9]+/g) || [];
      if (!terms.length || queryInput.value.length > 160) {
        status.textContent = "Enter a question (up to 160 characters) with at least one searchable word.";
        status.classList.add("error");
        results.replaceChildren();
        return;
      }
      const visibleDocuments = documents.filter((document) => document.scope === "public" || roleInput.value === document.scope);
      const ranked = visibleDocuments
        .map((document) => {
          const matches = [...new Set(terms)].filter((term) => document.words.includes(term));
          return { ...document, matches, score: matches.length };
        })
        .filter((document) => document.score > 0)
        .sort((left, right) => right.score - left.score || left.title.localeCompare(right.title))
        .slice(0, Number(topKInput.value));
      results.replaceChildren();
      status.classList.remove("error");
      if (!ranked.length) {
        const empty = document.createElement("p");
        empty.className = "empty-state";
        empty.textContent = "No in-scope passages matched. A grounded system should abstain or ask for clarification, not invent evidence.";
        results.append(empty);
        status.textContent = `${visibleDocuments.length} in-scope documents checked; no evidence retrieved.`;
        return;
      }
      ranked.forEach((passage, index) => {
        const article = document.createElement("article");
        article.className = "retrieval-card";
        const heading = document.createElement("h3");
        heading.textContent = `${index + 1}. ${passage.title}`;
        const source = document.createElement("p");
        source.className = "source-id";
        source.textContent = `Source: ${passage.id} · Toy overlap score: ${passage.score}/${new Set(terms).size}`;
        const text = document.createElement("p");
        text.textContent = passage.text;
        const matches = document.createElement("p");
        matches.className = "match-terms";
        matches.textContent = `Matched terms: ${passage.matches.join(", ")}`;
        article.append(heading, source, text, matches);
        results.append(article);
      });
      status.textContent = `${visibleDocuments.length} in-scope documents checked; ${ranked.length} passage(s) retrieved. Private passages were excluded before ranking.`;
    });
  }

  const agentLab = document.querySelector("#agent-policy-lab");
  if (agentLab) {
    const toolInput = agentLab.querySelector("#agent-tool");
    const budgetInput = agentLab.querySelector("#agent-budget");
    const budgetValue = agentLab.querySelector("#agent-budget-value");
    const approvalInput = agentLab.querySelector("#agent-approval");
    const status = agentLab.querySelector("[data-agent-status]");
    const checks = {
      allowlist: agentLab.querySelector('[data-policy-check="allowlist"]'),
      budget: agentLab.querySelector('[data-policy-check="budget"]'),
      approval: agentLab.querySelector('[data-policy-check="approval"]'),
      result: agentLab.querySelector('[data-policy-check="result"]'),
    };
    budgetInput.addEventListener("input", () => {
      budgetValue.value = budgetInput.value;
      budgetValue.textContent = budgetInput.value;
    });
    agentLab.querySelector('[data-agent-action="check"]').addEventListener("click", () => {
      const tool = toolInput.value;
      const budget = Number(budgetInput.value);
      const policy = {
        search: { name: "search_course", allowed: true, cost: 1, sideEffect: false },
        email: { name: "send_email", allowed: true, cost: 3, sideEffect: true },
        delete: { name: "delete_record", allowed: false, cost: 2, sideEffect: true },
      }[tool];
      const allow = policy.allowed;
      const withinBudget = budget >= policy.cost;
      const approved = !policy.sideEffect || (tool === "email" && approvalInput.checked);
      const passed = allow && withinBudget && approved;
      const checkResults = [
        ["allowlist", allow ? "Pass · tool is allow-listed" : "Fail · tool is not allow-listed", allow ? "pass" : "fail"],
        ["budget", !allow ? "Skipped · tool denied by allowlist" : withinBudget ? `Pass · ${policy.cost} step(s) fit` : `Fail · needs ${policy.cost} step(s)`, !allow ? "skip" : withinBudget ? "pass" : "fail"],
        ["approval", !allow ? "Skipped · tool denied by allowlist" : approved ? policy.sideEffect ? "Pass · explicit approval present" : "Pass · read-only tool" : "Fail · approval required", !allow ? "skip" : approved ? "pass" : "fail"],
        ["result", passed ? "Allow simulation only" : "Deny request", passed ? "pass" : "fail"],
      ];
      checkResults.forEach(([key, text, state]) => {
        const card = checks[key];
        card.querySelector("em").textContent = text;
        card.classList.toggle("is-pass", state === "pass");
        card.classList.toggle("is-fail", state === "fail");
        card.classList.toggle("is-skip", state === "skip");
      });
      status.classList.toggle("error", !passed);
      status.textContent = passed
        ? `Policy allows a mock ${policy.name} request. No tool was invoked and no external effect occurred.`
        : `Policy denies ${policy.name}. ${allow ? "Resolve the failed budget or approval check." : "Only explicitly allow-listed tools may run."}`;
    });
  }

  const releaseLab = document.querySelector("#delivery-lab");
  if (releaseLab) {
    const testsInput = releaseLab.querySelector("#release-tests");
    const healthInput = releaseLab.querySelector("#release-health");
    const status = releaseLab.querySelector("[data-release-status]");
    const nextButton = releaseLab.querySelector('[data-release-action="next"]');
    const nodes = Array.from(releaseLab.querySelectorAll("[data-release-node]"));
    const gate = releaseLab.querySelector("#release-gate");
    const exposure = releaseLab.querySelector("#release-exposure");
    const outcome = releaseLab.querySelector("#release-outcome");
    const stages = ["commit", "build", "tests", "approval", "canary", "health", "outcome"];
    let active = -1;
    let finished = false;
    let decision = "";

    const render = () => {
      nodes.forEach((node) => {
        const index = stages.indexOf(node.dataset.releaseNode);
        node.classList.toggle("is-active", index === active);
        node.classList.toggle("is-complete", index >= 0 && index < active);
        node.classList.toggle("is-fail", node.dataset.releaseNode === "tests" && decision === "stopped-tests");
        node.classList.toggle("is-rollback", node.dataset.releaseNode === "outcome" && decision === "rollback");
      });
      gate.textContent = active < 0 ? "—" : stages[active].toUpperCase();
      exposure.textContent = active >= stages.indexOf("canary") ? "5%" : "0%";
      outcome.textContent = decision === "promoted" ? "Promoted" : decision === "rollback" ? "Rolled back" : decision === "stopped-tests" ? "Stopped before deploy" : "Pending";
      nextButton.disabled = active < 0 || finished;
    };
    const advance = () => {
      if (active < 0 || finished) return;
      if (active === stages.indexOf("tests") && testsInput.value === "fail") {
        decision = "stopped-tests";
        finished = true;
        status.textContent = "Automated tests failed. The release stopped before approval and deployment.";
        render();
        return;
      }
      if (active === stages.indexOf("health")) {
        if (healthInput.value === "unhealthy") {
          active = stages.indexOf("outcome");
          decision = "rollback";
          finished = true;
          status.textContent = "Canary signals were unhealthy at 5% exposure. The simulation rolled back instead of promoting.";
          render();
          return;
        }
        active = stages.indexOf("outcome");
        decision = "promoted";
        finished = true;
        status.textContent = "Canary signals were healthy. The simulation promotes only after the health gate passes.";
        render();
        return;
      }
      active += 1;
      status.textContent = `Reached gate ${active + 1} of ${stages.length}: ${stages[active]}. Advance to inspect the next decision.`;
      render();
    };
    releaseLab.querySelector('[data-release-action="start"]').addEventListener("click", () => {
      active = 0;
      finished = false;
      decision = "";
      status.classList.remove("error");
      status.textContent = "Release trace started. Advance one gate at a time.";
      render();
    });
    nextButton.addEventListener("click", advance);
    releaseLab.querySelector('[data-release-action="reset"]').addEventListener("click", () => {
      active = -1;
      finished = false;
      decision = "";
      gate.textContent = "—";
      exposure.textContent = "0%";
      outcome.textContent = "Not started";
      nextButton.disabled = true;
      status.textContent = "Reset. Choose outcomes to simulate a release.";
      status.classList.remove("error");
      nodes.forEach((node) => node.classList.remove("is-active", "is-complete", "is-fail", "is-rollback"));
    });
  }

  const params = new URLSearchParams(window.location.search);
  const requestedLab = params.get("lab");
  if (requestedLab) {
    const target = Array.from(document.querySelectorAll("[data-lab]"))
      .find((lab) => lab.dataset.lab === requestedLab);
    if (target) {
      document.querySelectorAll("[data-lab]").forEach((lab) => {
        lab.hidden = lab !== target;
      });
      document.querySelectorAll("[data-filter]").forEach((button) => {
        button.setAttribute("aria-pressed", String(button.dataset.filter === requestedLab));
      });
    }
  }
})();
