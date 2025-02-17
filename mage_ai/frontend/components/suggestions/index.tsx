import { useMemo } from 'react';

import Accordion, { AccordionPanel } from '@oracle/components/Accordion';
import FeatureSetType from '@interfaces/FeatureSetType';
import Spacing from '@oracle/elements/Spacing';
import SuggestionRow from './SuggestionRow';
import TransformerActionType from '@interfaces/TransformerActionType';
import { getFeatureIdMapping } from '@utils/models/featureSet';
import { UNIT } from '@oracle/styles/units/spacing';

type SuggestionsProps = {
  addAction: (action: TransformerActionType) => void;
  featureSet: FeatureSetType;
  removeAction: (action: TransformerActionType) => void;
  removeSuggestion: (action: TransformerActionType) => void;
};

function Suggestions({
  addAction,
  featureSet,
  removeAction,
}: SuggestionsProps) {
  const {
    insights,
    pipeline,
    suggestions,
  } = featureSet || {};
  const {
    actions,
  } = pipeline || {};
  const features = insights?.[0]?.map(({ feature }) => feature) || [];
  const numberOfActions = useMemo(() => Array.isArray(actions) ? actions?.length : 0, [actions]);
  const featureIdMapping = useMemo(() => getFeatureIdMapping(featureSet), [featureSet]);

  return (
    <>
      {
        Array.isArray(actions) && actions?.map((action, idx) => {
          const {
            title,
            action_payload: {
              action_arguments,
            },
          } = action;

          return (
            <Spacing
              key={`${idx}-${title}`}
              mt={idx >= 1 ? 1 : 0}
            >
              <SuggestionRow
                action={action}
                border
                featureIdMapping={featureIdMapping}
                featureSetId={featureSet?.id}
                features={features}
                idx={idx}
                onClose={numberOfActions - 1 === idx
                  ? () => removeAction(action)
                  : null
                }
                showIdx
              />
            </Spacing>
          );
        })
      }

      {suggestions?.length >= 1 && (
        <Spacing mt={2}>
          <Accordion
            highlighted
            visibleMapping={{ 0: true }}
          >
            <AccordionPanel
              maxHeight={UNIT * 50}
              noBackground
              noPaddingContent
              title={`${suggestions.length} suggested actions`}
            >
              {suggestions.map((suggestion, idx) => {
                const { action_payload: { action_arguments } } = suggestion;

                return (
                  <SuggestionRow
                    action={suggestion}
                    featureIdMapping={featureIdMapping}
                    featureSetId={featureSet?.id}
                    features={features}
                    idx={idx}
                    key={`${idx}-${suggestion.title}`}
                    link={() => addAction(suggestion)}
                    saveAction={addAction}
                  />
                );
              })}
            </AccordionPanel>
          </Accordion>
        </Spacing>
      )}
    </>
  );
}

export default Suggestions;
