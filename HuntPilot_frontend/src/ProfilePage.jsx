import ProfileResumeUpload from './ProfileResumeUpload';

export default function ProfilePage() {
  return (
  <div className="container py-5">
    <div className="row justify-content-center">
      <div className="col-12 col-md-10 col-lg-8">
        <div className="card shadow-lg border-0 rounded-3">
          {/* Header */}
          <div className="card-header bg-primary text-white">
            <h4 className="mb-0 fw-bold">Your Profile</h4>
          </div>

          {/* Body */}
          <div className="card-body">
            <p className="text-muted mb-4">
              Upload your resume once, and we’ll use it to match you against every new job you add.
            </p>
            
            {/* Resume Upload Section */}
            <div className="p-3 bg-light rounded">
              <ProfileResumeUpload />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

}
