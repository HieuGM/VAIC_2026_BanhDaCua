package com.hanoiheart.dataapi.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDate;
import java.time.OffsetDateTime;

/**
 * Cache hiển thị thông tin bệnh nhân từ FHIR.
 * Không lưu bệnh án, đơn thuốc, xét nghiệm, kết quả khám.
 * Chỉ lưu: họ tên, giới tính, ngày sinh, điện thoại, CCCD ẩn.
 */
@Entity
@Table(name = "patients_profile_cache", schema = "hospital")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PatientProfileCache {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "fhir_patient_id", nullable = false, unique = true)
    private String fhirPatientId;

    @Column(name = "full_name")
    private String fullName;

    private String phone;

    @Column(name = "date_of_birth")
    private LocalDate dateOfBirth;

    private String gender;

    /** CCCD đã được ẩn một phần (ví dụ: ****123456) */
    @Column(name = "national_id_masked")
    private String nationalIdMasked;

    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private OffsetDateTime updatedAt;
}
