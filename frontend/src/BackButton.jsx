import React from 'react';
import {Button} from '@heroui/react';

export default function BackButton({children, className, onPress, isDisabled}) {
  return <Button type="button" variant="ghost" className={`rollcall-back${className ? ' ' + className : ''}`}
    onPress={onPress} isDisabled={isDisabled}>
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round"><path d="M20 12H4m7-7-7 7 7 7"/></svg>
    {children}
  </Button>;
}
