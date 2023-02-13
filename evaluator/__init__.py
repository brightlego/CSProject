"""The Evaluator for the graphical calculator.

It contains the only function in the evaluator subdirectory that should be used
externally.

Functions:
    evaluate(raw_text: str,
             width: int,
             height: int,
             x_range: tuple[int, int],
             y_range: tuple[int, int]) -> str:
        -- Returns the path of the graph created using those inputs

"""

import evaluator.parser
import evaluator.executor


def evaluate(raw_text, width, height, x_range, y_range):
    """Evaluates the raw_text and produces a graph

    Arguments:
        raw_text: str
            -- The raw text to be parsed
        width: int
            -- The width of the graph in pixels
        height: int
            -- The height of the graph in pixels
        x_range: tuple[float, float]
            -- The range of x-values plotted
        y_range: tuple[float, float]
            -- The range of y-values plotted

    Returns:
        path: str
            -- The location of the graph produced
    """
    # Create a parser for the raw text and parse it
    parser = evaluator.parser.Parser(raw_text)
    execution_trees = parser.parse()

    # Creates an executor from the parsed statements
    executor = evaluator.executor.Executor(execution_trees)

    # Returns the location of the graph produced when this is executed
    return executor.graph(width, height, x_range, y_range)
