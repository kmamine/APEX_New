import { useRef, useState } from 'react';
import { cn } from '../lib/cn';

interface ImageDropzoneProps {
  file: File | null;
  onChange: (file: File | null) => void;
}

export function ImageDropzone({ file, onChange }: ImageDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);
  const preview = file ? URL.createObjectURL(file) : null;

  const pick = (files: FileList | null) => {
    const next = files?.[0] ?? null;
    if (next && next.type.startsWith('image/')) onChange(next);
  };

  return (
    <div
      className={cn(
        'flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-6 text-center transition-colors',
        dragging ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-gray-400',
      )}
      onClick={() => inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        pick(e.dataTransfer.files);
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => pick(e.target.files)}
      />
      {preview ? (
        <div className="flex flex-col items-center gap-2">
          <img src={preview} alt="input preview" className="max-h-48 rounded-lg object-contain" />
          <span className="text-xs text-gray-500">{file?.name} — click to replace</span>
        </div>
      ) : (
        <div className="text-gray-500">
          <div className="text-3xl">📷</div>
          <p className="mt-1 text-sm font-medium">Drop a photo here or click to upload</p>
          <p className="text-xs">A clear, front-facing photo works best</p>
        </div>
      )}
    </div>
  );
}
