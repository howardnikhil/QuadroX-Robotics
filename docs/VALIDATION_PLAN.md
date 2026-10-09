# Validation plan

| ID | Test | Procedure | Status |
|---|---|---|---|
| QX-001 | Pure logic tests | `python3 -m pytest` | To run |
| QX-002 | ROS build | Build in sourced ROS 2 Jazzy workspace | To run |
| QX-003 | Topic inspection | Confirm names, rates and all 12 joints | To run |
| QX-004 | E-stop gate | Publish true to `/quadrox/estop`; verify neutral output and latch | To run |
| QX-005 | Stale command | Stop gait publisher; verify neutral output | To run |
| QX-006 | Joint bounds | Inject out-of-range and NaN commands in a test harness | To run |
| QX-007 | Model verification | Compare dimensions and joint axes against CAD | To run |
| QX-008 | Restrained hardware test | Verify power, current, direction and physical stop on fixture | Not started |
| QX-009 | Locomotion | Validate stability, contact, thermal behavior and power draw | Not started |

A successful software build is not evidence that a physical quadruped is stable or safe.
