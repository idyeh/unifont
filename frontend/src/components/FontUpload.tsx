import { Upload } from "lucide-react";

type Props = {
  onUpload: (file: File) => Promise<void>;
};

export function FontUpload({ onUpload }: Props) {
  return (
    <label className="upload-button">
      <Upload size={16} />
      Upload font
      <input
        type="file"
        accept=".ttf,.otf,.woff2"
        onChange={(event) => {
          const file = event.target.files?.[0];
          if (file) {
            void onUpload(file);
            event.currentTarget.value = "";
          }
        }}
      />
    </label>
  );
}

