import uuid
from decimal import Decimal

from sqlmodel import Session

from app.fitness.models import FitnessExercise, FitnessPlan

PLAN_IDS = {
    "胸": uuid.UUID("00000000-0000-4000-8000-000000000101"),
    "背": uuid.UUID("00000000-0000-4000-8000-000000000102"),
    "肩": uuid.UUID("00000000-0000-4000-8000-000000000103"),
    "臀腿": uuid.UUID("00000000-0000-4000-8000-000000000104"),
}


def seed_fitness_demo_data(db: Session) -> None:
    for sort_order, (name, plan_id) in enumerate(PLAN_IDS.items()):
        if db.get(FitnessPlan, plan_id) is None:
            db.add(FitnessPlan(id=plan_id, name=name, sort_order=sort_order))
    db.flush()

    chest_id = PLAN_IDS["胸"]
    fixtures = (
        (
            uuid.UUID("00000000-0000-4000-8000-000000000201"),
            "杠铃卧推",
            Decimal("80"),
            8,
        ),
        (
            uuid.UUID("00000000-0000-4000-8000-000000000202"),
            "上斜哑铃卧推",
            Decimal("25"),
            10,
        ),
    )
    for sort_order, (exercise_id, name, weight, reps) in enumerate(fixtures):
        if db.get(FitnessExercise, exercise_id) is None:
            db.add(
                FitnessExercise(
                    id=exercise_id,
                    plan_id=chest_id,
                    name=name,
                    default_weight=weight,
                    default_reps=reps,
                    sort_order=sort_order,
                )
            )
    db.commit()
