# Metrics Architecture - Crowd Due Dill

This document explains our dual metrics approach for comprehensive monitoring.

## Overview

We use **two complementary metrics systems**:

1. **Internal StatsCollector** - Application-specific metrics
2. **Prometheus + Grafana** - Production HTTP/system monitoring

## 📊 Internal Stats Collector (`src/core/stats_collector.py`)

**Purpose**: Application-specific metrics for development and AI system monitoring

**What it tracks**:
- 🧠 **Memory System**: Summary creation, context builds, toggles
- 📚 **Vectorstore Health**: Document counts, collection status
- 🎯 **Domain Manager**: Active domains, configuration changes
- 💾 **AI Performance**: Model response times, internal processing

**Usage**:
- Development debugging via console output
- Internal health checks and business logic
- AI system performance analysis
- Application-specific metrics not suitable for Prometheus

**Access**: 
```python
# In application code
rag_system.stats_collector.print_comprehensive_stats()

# Via command line
python -c "from src.main import print_stats; print_stats()"
```

## 🎯 Prometheus + Grafana (Production Monitoring)

**Purpose**: Production HTTP/system monitoring with alerting

**What it tracks**:
- 🌐 **HTTP Requests**: Response times, error rates, request counts
- 💻 **System Resources**: CPU, memory, disk usage
- 🐳 **Container Metrics**: Docker container performance
- 📧 **Alerting**: Email notifications for critical issues

**Usage**:
- Production monitoring and alerting
- Historical trend analysis
- Performance dashboards
- System health monitoring

**Access**:
- **Metrics Endpoint**: `https://crowd-reg.beautiful-apps.com/metrics`
- **Grafana Dashboards**: `https://monitoring.crowd-reg.beautiful-apps.com`

## 🔄 Why Both?

### Internal StatsCollector is ideal for:
- **AI-specific metrics** (vector search performance, memory usage)
- **Business logic tracking** (domain switches, user behaviors)
- **Development debugging** (immediate console feedback)
- **Application health** (internal component status)

### Prometheus is ideal for:
- **HTTP performance** (request/response metrics)
- **System monitoring** (server resources)
- **Production alerting** (email notifications)
- **Historical analysis** (time-series data)

## 🚀 Best Practices

### For Development:
```python
# Use internal stats for debugging
rag_system.stats_collector.print_comprehensive_stats()

# Check specific component health
memory_stats = stats_collector.get_memory_stats()
vectorstore_stats = stats_collector.get_vectorstore_stats(vectorstore)
```

### For Production:
- Monitor Grafana dashboards for system health
- Use Prometheus metrics for automated alerting
- Check `/metrics` endpoint for integration health
- Review email alerts for critical issues

### For Business Analysis:
- Use internal stats for AI performance insights
- Use Prometheus for user traffic patterns
- Combine both for comprehensive system understanding

## 📈 Metrics Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Application│    │ Internal Stats  │    │   Console/Logs  │
│                 │───▶│   Collector     │───▶│   Development   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         │              ┌─────────────────┐    ┌─────────────────┐
         └─────────────▶│   Prometheus    │───▶│     Grafana     │
                        │   /metrics      │    │   Production    │
                        │                 │    │   Dashboards    │
                        └─────────────────┘    └─────────────────┘
                                 │
                                 │              ┌─────────────────┐
                                 └─────────────▶│  Email Alerts   │
                                                │   Operations    │
                                                │                 │
                                                └─────────────────┘
```

## 🎯 Summary

- **Keep both systems** - they serve different purposes
- **Internal stats** = AI performance + development debugging  
- **Prometheus** = HTTP performance + production monitoring
- **Grafana** = Beautiful dashboards + email alerting
- **Together** = Comprehensive observability for AI applications 