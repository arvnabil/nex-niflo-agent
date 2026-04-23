graph LR
subgraph "🌐 Omnichannel Input"
T[Telegram Bot]
L[LibreChat UI]
end

    subgraph "🛡️ Nex Gateway (FastAPI)"
        G[Auth & Route Handler]
        M[Shared Context Memory]
    end

    subgraph "🧠 Brain: Sovereign Supervisor"
        S{Sovereign Router}
        P[WIB Timezone Filter]
    end

    subgraph "👥 The Nex Squad"
        A1[Nex Help Desk]
        A2[Nex Analyst]
        A3[Nex Web ACTiV]
        A4[Nex Productivity]
    end

    subgraph "⚙️ Skill Engine"
        SK1[Web Search: DuckDuckGo]
        SK2[Automation: n8n/Zoom]
        SK3[Knowledge: RAG DB]
    end

    %% Flowing
    T & L --> G
    G --> M
    M --> S
    S --> P
    P --> A1 & A2 & A3 & A4
    A1 & A2 & A3 & A4 --> SK1 & SK2 & SK3

    %% Response back
    SK1 & SK2 & SK3 -.-> |Observation| S
    S -.-> |Aggregated AI Response| G
    G -.-> |Streaming Markdown| T & L

    style S fill:#f96,stroke:#333,stroke-width:4px
    style G fill:#bbf,stroke:#333,stroke-width:2px
    style M fill:#dfd,stroke:#333,stroke-dasharray: 5 5
