import React from 'react';
import Content from '@theme-original/DocItem/Content';
import type ContentType from '@theme/DocItem/Content';
import type {WrapperProps} from '@docusaurus/types';
import ContentControls from '@site/src/components/ContentControls/ContentControls';

type Props = WrapperProps<typeof ContentType>;

export default function ContentWrapper(props: Props): JSX.Element {
  return (
    <>
      <ContentControls
        contentId={props.children.type.metadata?.id || 'unknown'}
        originalContent={props.children.type.metadata?.description || ''}
      />
      <Content {...props} />
    </>
  );
}
