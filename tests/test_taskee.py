def test_taskee_registers_init_tasks(initialized_taskee):
    """Taskee should store all tasks found during initialization."""
    assert len(initialized_taskee.manager.tasks) == 6
    assert len(initialized_taskee.manager.active_tasks) == 2
    assert len(initialized_taskee.manager.events) == 0
