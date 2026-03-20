class AlarmWebRTCCard extends HTMLElement {
  isTokenValid(token) {
    if (!token) return false;
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const now = Math.floor(Date.now() / 1000);
      return payload.exp > now + 30;
    } catch (e) {
      console.error("Invalid token format", e);
      return false;
    }
  }

  set hass(hass) {
    this._hass = hass;

    const entityId = this.config.entity;
    const stateObj = hass.states[entityId];

    if (!stateObj) {
      this.innerHTML = `
        <ha-card>
          <div style="padding: 16px; color: red">
            Entity not found: ${entityId}
          </div>
        </ha-card>`;
      return;
    }

    const attrs = stateObj.attributes;
    const config = attrs.webrtc_config;
    const isValid = config && this.isTokenValid(config.signallingServerToken);

    if ((!config || !isValid) && stateObj.state !== 'on' && !this._requesting) {
      this._requesting = true;
      this._hass.callService("camera", "turn_on", { entity_id: entityId });
      this.renderPlaceholder("Refreshing session...");
      return;
    }

    if (isValid && !this._connected && !this._connecting) {
      if (JSON.stringify(config) !== JSON.stringify(this._currentConfig)) {
        this._retried = false;
      }

      this._requesting = false;
      this.renderVideo();
      this.startStream(config);
    }
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error("You need to define an entity");
    }
    this.config = config;
  }

  renderPlaceholder(msg) {
    if (this._connected) return;
    this.innerHTML = `
      <ha-card>
        <div style="padding: 16px; text-align: center;">
          ${msg}
        </div>
      </ha-card>`;
  }

  renderVideo() {
    if (this.querySelector("video")) return;

    this.innerHTML = `
      <ha-card>
        <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; background: black;">
          <video id="video" autoplay playsinline muted style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;"></video>
        </div>
      </ha-card>
    `;
  }

  async startStream(config) {
    this._connecting = true;
    this._currentConfig = config;

    const pc = new RTCPeerConnection({
      iceServers: config.iceServers || []
    });
    this.pc = pc;

    const videoEl = this.querySelector("#video");

    const attemptPlay = async () => {
      if (videoEl.paused || videoEl.ended) {
        try {
          videoEl.muted = true;
          await videoEl.play();
        } catch (e) {
          console.warn("[AlarmWebRTC] Play failed:", e);
        }
      }
    };

    const startPlayLoop = () => {
      let attempts = 0;
      const interval = setInterval(() => {
        if (!this._connected) {
          clearInterval(interval);
          return;
        }
        if (!videoEl.paused && videoEl.currentTime > 0) {
          clearInterval(interval);
          return;
        }
        attempts++;
        attemptPlay();
        if (attempts > 10) clearInterval(interval);
      }, 1000);
    };

    pc.ontrack = (event) => {
      videoEl.srcObject = event.streams[0];
      startPlayLoop();
      this._connected = true;
      this._connecting = false;
    };

    document.addEventListener("visibilitychange", () => {
      if (document.visibilityState === "visible" && this._connected) {
        attemptPlay();
      }
    });

    pc.onicecandidate = (event) => {
      if (event.candidate && this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({
          to: this.remoteId,
          ice: event.candidate
        }));
      }
    };

    const wsUrl = `${config.signallingServerUrl}/${config.signallingServerToken}`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      this.ws.send("HELLO 2.0.1");
    };

    this.ws.onmessage = async (event) => {
      const msg = event.data;

      if (msg.startsWith("HELLO")) {
        this.ws.send(`START_SESSION ${config.cameraAuthToken}`);
        return;
      }

      if (msg.startsWith("SESSION_STARTED")) {
        return;
      }

      let data;
      try { data = JSON.parse(msg); } catch { return; }

      if (data.sdp?.type === "offer") {
        this.remoteId = data.from;
        const myId = data.to;

        await pc.setRemoteDescription(data.sdp);
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);

        this.ws.send(JSON.stringify({
          to: this.remoteId,
          from: myId,
          sdp: pc.localDescription
        }));
      }

      if (data.ice) {
        await pc.addIceCandidate(data.ice);
      }
    };

    this.ws.onclose = () => {
      if (!this._connected && !this._retried) {
        this._retried = true;
        this._connecting = false;
        this._hass.callService("camera", "turn_on", { entity_id: this.config.entity });
        this._currentConfig = null;
        return;
      }

      this._connected = false;
      this._connecting = false;
    };
  }

  disconnectedCallback() {
    if (this.pc) this.pc.close();
    if (this.ws) this.ws.close();
  }
}

customElements.define('alarm-webrtc-card', AlarmWebRTCCard);
