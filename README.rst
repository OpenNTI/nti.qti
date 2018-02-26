=======
nti.qti
=======
This project is focused on creating a tool to export QTI packages.

Below is a table showing how QTI maps to NTI, an "X" means that no equivalent exists.

----

+--------------------------------------+------------------------------------+
| Question Types in QTI:               | Question Types in NTI:             |
+======================================+====================================+
| choiceInteraction (single answer)    | MultipleChoicePart                 |
+--------------------------------------+------------------------------------+
| choiceInteraction (multiple answers) | MultipleChoiceMultipleAnswerPart   |
+--------------------------------------+------------------------------------+
| orderInteraction                     | X                                  |
+--------------------------------------+------------------------------------+
| associateInteraction                 | X                                  |
+--------------------------------------+------------------------------------+
| matchInteraction                     | MatchingPart, OrderingPart         |
+--------------------------------------+------------------------------------+
| gapMatchInteraction                  | X                                  |
+--------------------------------------+------------------------------------+
| inlineChoiceInteraction              | FillInTheBlankWithWordBankPart     |
+--------------------------------------+------------------------------------+
| textEntryInteraction                 | FreeResponsePart, SymbolicMathPart |
+--------------------------------------+------------------------------------+
| extendedTextInteraction              | ModeledContentPart                 |
+--------------------------------------+------------------------------------+
| hottextInteraction                   | X                                  |
+--------------------------------------+------------------------------------+
| hotspotInteraction                   | X                                  |
+--------------------------------------+------------------------------------+
| selectPointInteraction               | X                                  |
+--------------------------------------+------------------------------------+
| graphicOrderInteraction              | X                                  |
+--------------------------------------+------------------------------------+
| graphicAssociateInteraction          | X                                  |
+--------------------------------------+------------------------------------+
| positionObjectInteraction            | X                                  |
+--------------------------------------+------------------------------------+
| sliderInteraction                    | X                                  |
+--------------------------------------+------------------------------------+
| drawingInteraction                   | X                                  |
+--------------------------------------+------------------------------------+
| uploadInteraction                    | FilePart                           |
+--------------------------------------+------------------------------------+

----

The QTI implementation guide can be found here_.

.. _here: http://www.imsglobal.org/question/qtiv2p2/imsqti_v2p2_impl.html
