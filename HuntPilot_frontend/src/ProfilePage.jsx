import ProfileResumeUpload from './ProfileResumeUpload';

export default function ProfilePage() {
  return (
    <>
      <div className="container py-5">
        <div className="row justify-content-center">
          <div className="col-md-8">
            <div className="card shadow-sm">
              <div className="card-header bg-primary text-white">
                <h4 className="mb-0">Your Profile</h4>
              </div>
              <div className="card-body">
                <p className="text-muted mb-4">
                  Upload your resume once and we’ll use it to match you against every new job you add.
                </p>
                <ProfileResumeUpload />
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
