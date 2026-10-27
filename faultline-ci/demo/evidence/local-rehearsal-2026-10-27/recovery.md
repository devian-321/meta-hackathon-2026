# FaultLine CI — local rehearsal

**Real local Git commits and pytest runs. Scripted repair; GitLab Duo was not run.**

| Stage | Passed tests | Failed tests | Commit |
| --- | --- | --- | --- |
| Healthy baseline | 8 | 0 | `e6e74fe645a26145e3b1d170c833962768bbac9c` |
| Injected fault | 5 | 3 | `cece36330b1d5579b062caa03cecd817060f581d` |
| Scripted fixture restoration | 8 | 0 | `5743bdc699670004b9241f0e8ccb55a103a57cf9` |
| Tampered assertions (false green) | 8 | 0 | `973602d2ab5a4a7832df4c5741a44a73a3caa6b2` |

Repository guard accepts the exact repair and rejects the tampered tests.

Commit ancestry and code scope were checked against real local Git objects. The bundled Git history preserves the proof. Native Duo, hosted pipelines, and human approval remain pending.

Measured durations cover local pytest subprocesses only.
