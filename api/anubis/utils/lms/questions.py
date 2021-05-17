import random
from typing import List, Dict

from anubis.models import (
    db,
    Assignment,
    AssignmentQuestion,
    AssignedStudentQuestion,
    User,
    InCourse,
)
from anubis.utils.data import _verify_data_shape, is_debug
from anubis.utils.services.cache import cache


def get_question_sequence_mapping(
        questions: List[AssignmentQuestion],
) -> Dict[int, List[AssignmentQuestion]]:
    """
    Get mapping of sequence to question mapping from list of questions

    response = {
      1 : [
        AssignmentQuestion,
        ...
      ]
    }

    :param questions:
    :return:
    """

    # Get unique sequences
    sequences = set(question.sequence for question in questions)

    # Build up sequence to question mapping
    sequence_to_questions = {sequence: [] for sequence in sequences}
    for question in questions:
        sequence_to_questions[question.sequence].append(question)

    return sequence_to_questions


def hard_reset_questions(assignment: Assignment):
    """
    Hard reset all questions for a given assignment. This
    will delete question assignments and the questions
    themselves.

    :param assignment:
    :return:
    """

    # Delete the student question assignments
    AssignedStudentQuestion.query.filter(
        AssignedStudentQuestion.assignment_id == assignment.id
    ).delete()

    # Delete the questions themselves
    AssignmentQuestion.query.filter(
        AssignmentQuestion.assignment_id == assignment.id
    ).delete()

    # commit the delete
    db.session.commit()


def assign_questions(assignment: Assignment):
    """
    Assign existing questions to students for a given assignment.

    * This will reset question assignments when called *

    :param assignment:
    :return:
    """

    # Delete any existing question assignments
    AssignedStudentQuestion.query.filter(
        AssignedStudentQuestion.assignment_id == assignment.id
    ).delete()

    # Find the questions that have been created for this assignment
    raw_questions = AssignmentQuestion.query.filter(
        AssignmentQuestion.assignment_id == assignment.id,
    ).all()

    questions = get_question_sequence_mapping(raw_questions)

    # Go through students in the class and assign them questions
    assigned_questions = []
    students = (
        User.query.join(InCourse)
            .filter(InCourse.course_id == assignment.course_id)
            .all()
    )
    for student in students:
        for sequence, qs in questions.items():
            # Get a random question from the pool at this sequence
            selected_question = random.choice(qs)

            # Assign them the question
            assigned_question = AssignedStudentQuestion(
                owner=student,
                assignment=assignment,
                question=selected_question,
            )
            assigned_questions.append(assigned_question.data)
            db.session.add(assigned_question)

    # Commit assignments
    db.session.commit()

    return assigned_questions


def ingest_questions(questions: dict, assignment: Assignment):
    """
    questions: [
      {
        sequence: int
        questions: [
          {
            q: str // what is 2*2
            a: str // 4
          },
        ]
      },
      ...
    ]

    response = {
      rejected: [ ... ]
      ignored: [ ... ]
      accepted: [ ... ]
    }

    :param questions:
    :param assignment:
    :return:
    """

    question_shape = {"questions": {"q": str, "a": str}, "sequence": int}

    if questions is None:
        return

    # Iterate over questions
    rejected, ignored, accepted = [], [], []
    for question_sequence in questions:
        shape_good, err_path = _verify_data_shape(question_sequence, question_shape)
        if not shape_good:
            # Reject the question if the shape is bad and continue
            rejected.append(
                {
                    "question": question_sequence,
                    "reason": "could not verify data shape " + err_path,
                }
            )
            continue

        sequence = question_sequence["sequence"]
        for question in question_sequence["questions"]:

            # Check to see if question already exists for the current
            # assignment
            exists = AssignmentQuestion.query.filter(
                AssignmentQuestion.assignment_id == assignment.id,
                AssignmentQuestion.question == question["q"],
            ).first()
            if exists is not None:
                # If the question exists, ignore it and continue
                ignored.append({"question": question, "reason": "already exists"})
                continue

            # Create the new question from posted data
            assignment_question = AssignmentQuestion(
                assignment_id=assignment.id,
                question=question["q"],
                solution=question["a"],
                sequence=sequence,
            )
            db.session.add(assignment_question)
            accepted.append({"question": question})

    # Commit additions
    db.session.commit()

    return accepted, ignored, rejected


def get_all_questions(assignment: Assignment) -> List[Dict[str, str]]:
    """
    Get all questions for a given assignment.

    response = [
      {
        question: "what is 2*2?",
        solution: "4",
        ...
      },
      ...
    ]

    :param assignment:
    :return:
    """

    # Get all questions
    questions = AssignmentQuestion.query.filter(
        AssignmentQuestion.assignment_id == assignment.id
    ).all()

    # Get sequence to question mapping
    sequence_to_questions = get_question_sequence_mapping(questions)

    # Get the raw questions in a generator of lists
    question_sequences = sequence_to_questions.values()

    # Pull questions out of sequences and add
    # them to question_list
    questions_list: List[Dict[str, str]] = []
    for sequence in question_sequences:
        for q in sequence:
            questions_list.append(q.full_data)

    return questions_list


@cache.memoize(timeout=5, unless=is_debug)
def get_assigned_questions(assignment_id: str, user_id: str, full: bool = False):
    """
    Get the assigned question objects for a user_id and assignment.

    If the full option is on, then a full view (including solutions) will be returned

    * The results are lightly cached *

    :param assignment_id:
    :param user_id:
    :param full:
    :return:
    """

    # Get assigned questions
    assigned_questions = AssignedStudentQuestion.query.filter(
        AssignedStudentQuestion.assignment_id == assignment_id,
        AssignedStudentQuestion.owner_id == user_id,
    ).all()

    if not full:
        return [assigned_question.data for assigned_question in assigned_questions]
    return [assigned_question.full_data for assigned_question in assigned_questions]
