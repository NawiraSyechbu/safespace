const posts = [
  {
    id: 1,
    community: "Technology",
    author: "alex",
    title: "How is AI changing the way we learn?",
    content:
      "I'd love to hear everyone's perspective on AI in education.",
  },
  {
    id: 2,
    community: "Campus Life",
    author: "sarah",
    title: "What's your best advice for new students?",
    content:
      "Share something you wish you knew during your first year.",
  },
];

function CommunityFeed() {
  return (
    <main style={{ maxWidth: "800px", margin: "40px auto", padding: "20px" }}>
      <h1>Community Feed</h1>
      <p>Explore conversations from the SafeSpace community.</p>

      {posts.map((post) => (
        <article
          key={post.id}
          style={{
            border: "1px solid #e5e5e5",
            borderRadius: "16px",
            padding: "24px",
            marginTop: "20px",
          }}
        >
          <small>{post.community} · @{post.author}</small>
          <h2>{post.title}</h2>
          <p>{post.content}</p>
        </article>
      ))}
    </main>
  );
}

export default CommunityFeed;