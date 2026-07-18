package com.hanoiheart.dataapi.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.OffsetDateTime;

/**
 * Bảng liên kết User (auth) ↔ FHIR Patient ID.
 * Backend dùng bảng này để xác định bệnh nhân sau khi xác thực JWT.
 * Frontend KHÔNG BAO GIỜ nhận hoặc truyền fhir_patient_id.
 */
@Entity
@Table(name = "user_patient_links", schema = "hospital")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserPatientLink {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    /** FHIR Patient ID — chỉ backend được biết. */
    @Column(name = "fhir_patient_id", nullable = false)
    private String fhirPatientId;

    /** self / spouse / child / parent / other */
    @Column(nullable = false)
    @Builder.Default
    private String relationship = "self";

    @Column(name = "is_primary", nullable = false)
    @Builder.Default
    private Boolean isPrimary = true;

    @Column(name = "verified_at")
    private OffsetDateTime verifiedAt;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private OffsetDateTime createdAt;
}
