============
nti.qti
============
This project is focused on creating a tool to export QTI packages.

Below is a table showing how QTI maps to NTI, an "X" means that no equivalent exists.

+--------------------------------------+----------------------------------+
| Question Types in QTI:               | Question Types in NTI:           |
+======================================+==================================+
| choiceInteraction (single answer)    | MultipleChoicePart               |
+--------------------------------------+----------------------------------+
| choiceInteraction (multiple answers) | MultipleChoiceMultipleAnswerPart |
+--------------------------------------+----------------------------------+
| orderInteraction                     | OrderingPart                     |
+--------------------------------------+----------------------------------+
| associateInteraction                 | X                                |
+--------------------------------------+----------------------------------+
| matchInteraction                     | MatchingPart                     |
+--------------------------------------+----------------------------------+
| gapMatchInteraction                  | X                                |
+--------------------------------------+----------------------------------+
| inlineChoiceInteraction              | FillInTheBlankWithWordBankPart   |
+--------------------------------------+----------------------------------+
| textEntryInteraction                 | FreeResponsePart                 |
+--------------------------------------+----------------------------------+
| extendedTextInteraction              | ModeledContentPart               |
+--------------------------------------+----------------------------------+
| hottextInteraction                   | X                                |
+--------------------------------------+----------------------------------+
| hotspotInteraction                   | X                                |
+--------------------------------------+----------------------------------+
| selectPointInteraction               | X                                |
+--------------------------------------+----------------------------------+
| graphicOrderInteraction              | X                                |
+--------------------------------------+----------------------------------+
| graphicAssociateInteraction          | X                                |
+--------------------------------------+----------------------------------+
| positionObjectInteraction            | X                                |
+--------------------------------------+----------------------------------+
| sliderInteraction                    | X                                |
+--------------------------------------+----------------------------------+
| drawingInteraction                   | X                                |
+--------------------------------------+----------------------------------+
| uploadInteraction                    | FilePart                         |
+--------------------------------------+----------------------------------+
| textEntryInteraction (using LaTeX)   | SymbolicMathPart                 |
+--------------------------------------+----------------------------------+